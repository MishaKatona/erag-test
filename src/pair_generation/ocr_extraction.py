from pdf2image import convert_from_bytes
import pytesseract
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from time import perf_counter
import json

# controls the page segmentation mode
# see https://nanonets.com/blog/ocr-with-tesseract/ for more information
# mode 3 - Fully automatic page segmentation. (Default)
# mode 6 - Assume a single uniform block of text.
# ALL tesseract settings https://muthu.co/all-tesseract-ocr-options/
TESSERACT_CONFIG = '--psm 3 tessedit_do_invert=0'

# If you don't have tesseract executable in your PATH, include the following:
# pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'


def _image_to_str(image, config) -> str:
    print("*", end="")
    return str(pytesseract.image_to_string(
        image=image,
        config=config)
    )


class OCRDocument:
    def __init__(self,
                 pdf_doc: bytes,
                 use_multiprocess_ocr: bool = True):
        # move this so that I only convert the pages that I need
        self.pdf_doc = convert_from_bytes(pdf_doc, thread_count=8, grayscale=True)
        self.number_of_pages = len(self.pdf_doc)
        self.use_multiprocess_ocr = use_multiprocess_ocr
        self.processed_pages = dict()

    def get_all_pages(self) -> dict[int, str]:
        """
        Returns a dictionary with they key being the page number and the
        value being the text on that page
        """
        page_numbers = list(range(self.number_of_pages))
        return self._retrieve_pages_str(page_numbers)

    def get_pages(self, start: int, num_pages: int) -> dict[int, str]:

        if start < 0 or start >= self.number_of_pages:
            raise Exception(f"Invalid start page number: {start}")
        if start + num_pages > self.number_of_pages:
            print(f"Warning: Requested {num_pages} pages starting from page "
                  f"{start}, but document only has {self.number_of_pages} pages.")
            num_pages = self.number_of_pages - start

        page_numbers = list(range(start, start + num_pages))
        return self._retrieve_pages_str(page_numbers)

    def _retrieve_pages_str(self,
                            requested_page_numbers: list[int]
                            ) -> dict[int, str]:
        # Creates dict with all pages, value is None if it hasn't been processed
        pages = {
            page_number: self.processed_pages.get(page_number) 
            for page_number in requested_page_numbers
        }
        
        page_numbers_to_ocr = [
            page_num for page_num, string in pages.items() if string is None
        ]

        # Multiprocessing overhead might now be worth it if we have 2 cores
        # This will currently use as many as it can
        if len(page_numbers_to_ocr) > 1 and self.use_multiprocess_ocr:
            pages.update(self._multi_process_ocr(page_numbers_to_ocr))
        else:
            pages.update(self._single_process_ocr(page_numbers_to_ocr))

        self.processed_pages.update(pages)

        return pages

    def _single_process_ocr(self, page_numbers: list[int]) -> dict[int, str]:
        """
        Returns a dictionary with the key being the page number and the
        value being the text on that page. Uses a single processor.
        """
        pages = {}

        for page_number in page_numbers:
            image = self.pdf_doc[page_number]
            pages[page_number] = _image_to_str(image, TESSERACT_CONFIG)

        return pages

    def _multi_process_ocr(self, page_numbers: list[int]) -> dict[int, str]:
        """
        Returns a dictionary with the key being the page number and the
        value being the text on that page. Uses multiprocessing for faster processing.
        """
        pages = {}

        images = [self.pdf_doc[page_number] for page_number in page_numbers]

        print("*" * len(images))

        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            results = list(executor.map(
                _image_to_str, images, [TESSERACT_CONFIG] * len(images)
            ))

        for idx, result in enumerate(results):
            pages[page_numbers[idx]] = result

        return pages


def extract_text_as_pages(doc_name):

    print(f"Reading pdf document: {doc_name}")
    with open(f"documents/{doc_name}.pdf", "rb") as f:
        data = f.read()

    print(f"Converting to images")
    s = perf_counter()
    t_doc = OCRDocument(data, use_multiprocess_ocr=True)
    print(perf_counter() - s)

    print(f"Starting OCR")
    s = perf_counter()
    pages = t_doc.get_all_pages()
    t = perf_counter() - s
    print(f"\nOCR took {t} seconds, {t / len(pages)} seconds per page")

    print(f"Saving as json to")
    with open(f"ocr_output/{doc_name}.json", "w") as f:
        json.dump(pages, f, indent=4)

    return pages


if __name__ == "__main__":
    # name = "Fundamental_Concepts_Liquid_Rocket_Engines"
    name = "Handbook_Space_Technology"

    extract_text_as_pages(name)


