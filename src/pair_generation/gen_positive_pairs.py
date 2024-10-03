from src.llm.api_wrappers import OpenaiAPI
from src.llm.tools.question_tool import QuestionTool
import pypdf
from PyPDF2 import PdfReader
import json
import csv
import io
from re import sub
import pandas as pd
from time import perf_counter


def format_pages_json(ocr_json: dict) -> str:
    text = ""
    for page_num, page_text in ocr_json.items():
        page_text = sub(r"\n\n", "DOUBLE_NEWLINE", page_text)
        # remove newlines
        page_text = sub(r"\n", " ", page_text)
        # change DOUBLE_NEWLINE back to \n
        page_text = sub(r"DOUBLE_NEWLINE", "\n", page_text)

        text += page_text

    return text


def create_chunks(txt, chunk_size=800, min_section_size=50) -> list[str]:
    sections = txt.split("\n")
    chunks = []
    current_chunk = ""
    while sections:
        section = sections.pop(0)
        if len(section) < min_section_size:
            continue
        # if the current section + the previous section is less than the chunk size
        # append the current section to the current chunk
        if len(current_chunk) + len(section) <= chunk_size:
            current_chunk += section
            continue
        # if the current_chunk would exceed the chunk size with the addition of
        # the current section then append the current_chunk to the chunks list
        elif current_chunk:
            chunks.append(current_chunk)
            current_chunk = ""

        # if the section is smaller than the chunk size but the next section would
        # exceed the chunk size then just append to chunks
        if len(section) <= chunk_size:
            chunks.append(section)
        else:
            sentences = section.split(". ")
            while sentences:
                sentence = sentences.pop(0)
                current_chunk += sentence + ". "
                if len(current_chunk) > chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = ""
            if current_chunk:
                # if the remainder is less than 1/3 of the chunk size
                # then just add it to the last chunk
                if len(current_chunk) <= chunk_size / 3:
                    chunks[-1] += current_chunk
                else:
                    chunks.append(current_chunk)
                current_chunk = ""

    return chunks


def get_async_questions(api, contexts: list[str]
                        ) -> (list[str], list[str], list[str], list[str]):

    system_prompt = (
        "You are a Teacher/Professor. Your task is to create a question "
        "for an upcoming quiz/examination. The questions should be "
        "technical in nature. Restrict the questions to the context "
        "information provided. Only use the context and no prior "
        "knowledge to generate the questions. Base your question on "
        "information specific to the context. Only ask questions that "
        "are clearly stated in the context. The question should be at "
        "most 30 words long. Avoid using the same phrases as in the "
        "context as this could give hints to the answer. The students "
        "won't see the context so it is important that the question does "
        "not reference the context in any way. Make sure to spell each "
        "word correctly in the question, they should be valid English words."
    )

    responses = api.get_async_tool_response(contexts,
                                            system_prompt,
                                            [QuestionTool])

    questions, qualities, technical_levels, out_contexts = [], [], [], []
    for idx, response in enumerate(responses):
        output = response.get_as_dict()
        if output is None:
            print("Error: could not parse response to dict")
            continue
        question = output.get("Question")
        quality = output.get("Good_Quality")
        technical_level = output.get("Technical_Level")
        if question is None or quality is None or technical_level is None:
            print("Error: missing question or quality")
            continue
        questions.append(question)
        qualities.append(quality)
        technical_levels.append(technical_level)
        out_contexts.append(contexts[idx])

    return questions, qualities, technical_levels, out_contexts


def gen_llm_pairs(chunks: list[str]):
    api = OpenaiAPI(model_name='gpt-4o-mini')

    print("Generating positive pairs")

    anchor, quality, t_levels, positive = [], [], [], []
    num_async = 10
    print("*" * (len(chunks) // num_async // 10))
    s = perf_counter()
    for i in range(0, len(chunks) - 1, num_async):
        if (i // num_async) % 10 == 0:
            print("*", end="")
        question_chunks = chunks[i:i + num_async]
        questions, qualities, t_level, contexts = get_async_questions(api, question_chunks)
        anchor.extend(questions)
        quality.extend(qualities)
        positive.extend(contexts)
        t_levels.extend(t_level)
    print(f"\nTime taken: {perf_counter() - s:.2f} seconds")

    return anchor, positive, quality, t_levels


def save_as_csv(anchor, positive, quality, t_levels, path):
    data = [anchor, positive, quality, t_levels]
    df = pd.DataFrame(data).T
    df = df.rename(columns={0: "anchor", 1: "positive", 2: "quality", 3: "technical_level"})
    df.to_csv(path + ".csv", index=False)


def gen_and_save_positive_pairs_from_ocr_dict(ocr_dict: dict,
                                              output_path: str,
                                              chunk_size: int = 400):
    text = format_pages_json(ocr_dict)
    chunks = create_chunks(text, chunk_size=chunk_size)
    anchor, positive, quality, t_level = gen_llm_pairs(chunks)
    save_as_csv(anchor, positive, quality, t_level, output_path)
