from pdf2image import convert_from_bytes
from tesserocr import PyTessBaseAPI, PSM
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from time import perf_counter
import json

# Tesseract configuration
TESSERACT_PSM = PSM.AUTO


def _image_to_str(image, psm_mode) -> str:
    with PyTessBaseAPI(psm=psm_mode) as api:
        api.SetImage(image)
        text = api.GetUTF8Text()
    return text


class OCRDocument:
    def __init__(self, pdf_doc: bytes, use_multiprocess_ocr: bool = True):
        # Convert PDF to images
        self.pdf_doc = convert_from_bytes(pdf_doc, thread_count=8, grayscale=True)
        self.number_of_pages = len(self.pdf_doc)
        self.use_multiprocess_ocr = use_multiprocess_ocr
        self.processed_pages = dict()

    def get_all_pages(self) -> dict[int, str]:
        page_numbers = list(range(self.number_of_pages))
        return self._retrieve_pages_str(page_numbers)

    def get_pages(self, start: int, num_pages: int) -> dict[int, str]:
        if start < 0 or start >= self.number_of_pages:
            raise Exception(f"Invalid start page number: {start}")
        if start + num_pages > self.number_of_pages:
            print(f"Warning: Requested {num_pages} pages starting from page {start}, "
                  f"but document only has {self.number_of_pages} pages.")
            num_pages = self.number_of_pages - start

        page_numbers = list(range(start, start + num_pages))
        return self._retrieve_pages_str(page_numbers)

    def _retrieve_pages_str(self, requested_page_numbers: list[int]) -> dict[int, str]:
        pages = {page_number: self.processed_pages.get(page_number) for page_number in requested_page_numbers}
        page_numbers_to_ocr = [page_num for page_num, string in pages.items() if string is None]

        if len(page_numbers_to_ocr) > 1 and self.use_multiprocess_ocr:
            pages.update(self._multi_process_ocr(page_numbers_to_ocr))
        else:
            pages.update(self._single_process_ocr(page_numbers_to_ocr))

        self.processed_pages.update(pages)
        return pages

    def _single_process_ocr(self, page_numbers: list[int]) -> dict[int, str]:
        pages = {}
        with PyTessBaseAPI(psm=PSM.SINGLE_BLOCK) as api:
            for page_number in page_numbers:
                image = self.pdf_doc[page_number]
                api.SetImage(image)
                pages[page_number] = api.GetUTF8Text()

        return pages

    def _multi_process_ocr(self, page_numbers: list[int]) -> dict[int, str]:
        pages = {}
        images = [self.pdf_doc[page_number] for page_number in page_numbers]

        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            results = list(executor.map(_image_to_str, images, [TESSERACT_PSM] * len(images)))

        for idx, result in enumerate(results):
            pages[page_numbers[idx]] = result

        return pages


if __name__ == "__main__":
    with open("../ocr/documents/Fundamental_Concepts_Liquid_Rocket_Engines.pdf", "rb") as f:
        data = f.read()

    s = perf_counter()
    t_doc = OCRDocument(data, use_multiprocess_ocr=False)
    print(perf_counter() - s)

    s = perf_counter()
    pages = t_doc.get_all_pages()
    t = perf_counter() - s
    print(f"\nOCR took {t} seconds, {t / len(pages)} seconds per page")

    # Optionally save to json
    # with open("output.json", "w") as f:
    #     json.dump(pages, f)