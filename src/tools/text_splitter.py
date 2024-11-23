from typing import Dict, List, Tuple, TypedDict
import re
import tiktoken


# Usage:
# Initialize splitter and process text
# splitter = TextSplitter()
# chunks = await splitter.split(text, 1000)


class Metadata(TypedDict):
    tokens: int
    headers: Dict[str, List[str]]
    urls: List[str]
    images: List[str]


class Doc(TypedDict):
    text: str
    metadata: Metadata


class TextSplitter:
    def __init__(self, model_name: str = "gpt-4o") -> None:
        self.model_name = model_name
        self.tokenizer = tiktoken.encoding_for_model(model_name)
        self.special_tokens = {
            "<|im_start|>": 100264,
            "<|im_end|>": 100265,
            "<|im_sep|>": 100266,
        }

    async def initialize_tokenizer(self) -> None:
        if not self.tokenizer:
            self.tokenizer = await tiktoken.encoding_for_model(self.model_name)

    def count_tokens(self, text: str) -> int:
        if not self.tokenizer:
            raise RuntimeError("Tokenizer not initialized")
        formatted_content = self.format_for_tokenization(text)
        return len(
            self.tokenizer.encode(
                formatted_content,
                allowed_special={"<|im_start|>", "<|im_sep|>", "<|im_end|>"},
            )
        )

    def format_for_tokenization(self, text: str) -> str:
        return f"<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant<|im_end|>"

    async def split(self, text: str, limit: int) -> List[Doc]:
        print(f"Starting split process with limit: {limit} tokens")
        await self.initialize_tokenizer()
        chunks: List[Doc] = []
        position = 0
        total_length = len(text)
        current_headers: Dict[str, List[str]] = {}

        while position < total_length:
            print(f"Processing chunk starting at position: {position}")
            chunk_text, chunk_end = self.get_chunk(text, position, limit)
            tokens = self.count_tokens(chunk_text)
            print(f"Chunk tokens: {tokens}")

            headers_in_chunk = self.extract_headers(chunk_text)
            self.update_current_headers(current_headers, headers_in_chunk)

            content, urls, images = self.extract_urls_and_images(chunk_text)

            chunks.append(
                {
                    "text": content,
                    "metadata": {
                        "tokens": tokens,
                        "headers": dict(current_headers),
                        "urls": urls,
                        "images": images,
                    },
                }
            )

            print(f"Chunk processed. New position: {chunk_end}")
            position = chunk_end

        print(f"Split process completed. Total chunks: {len(chunks)}")
        return chunks

    def get_chunk(self, text: str, start: int, limit: int) -> Tuple[str, int]:
        print(f"Getting chunk starting at {start} with limit {limit}")

        overhead = self.count_tokens(
            self.format_for_tokenization("")
        ) - self.count_tokens("")

        end = min(
            start + int((len(text) - start) * limit / self.count_tokens(text[start:])),
            len(text),
        )

        chunk_text = text[start:end]
        tokens = self.count_tokens(chunk_text)

        while tokens + overhead > limit and end > start:
            print(
                f"Chunk exceeds limit with {tokens + overhead} tokens. Adjusting end position..."
            )
            end = self.find_new_chunk_end(text, start, end)
            chunk_text = text[start:end]
            tokens = self.count_tokens(chunk_text)

        end = self.adjust_chunk_end(text, start, end, tokens + overhead, limit)

        chunk_text = text[start:end]
        tokens = self.count_tokens(chunk_text)
        print(f"Final chunk end: {end}")
        return chunk_text, end

    def adjust_chunk_end(
        self, text: str, start: int, end: int, current_tokens: int, limit: int
    ) -> int:
        min_chunk_tokens = int(limit * 0.8)

        next_newline = text.find("\n", end)
        prev_newline = text.rfind("\n", start, end)

        if next_newline != -1 and next_newline < len(text):
            extended_end = next_newline + 1
            chunk_text = text[start:extended_end]
            tokens = self.count_tokens(chunk_text)
            if tokens <= limit and tokens >= min_chunk_tokens:
                print(f"Extending chunk to next newline at position {extended_end}")
                return extended_end

        if prev_newline > start:
            reduced_end = prev_newline + 1
            chunk_text = text[start:reduced_end]
            tokens = self.count_tokens(chunk_text)
            if tokens <= limit and tokens >= min_chunk_tokens:
                print(f"Reducing chunk to previous newline at position {reduced_end}")
                return reduced_end

        return end

    def find_new_chunk_end(self, text: str, start: int, end: int) -> int:
        new_end = end - int((end - start) / 10)
        if new_end <= start:
            new_end = start + 1
        return new_end

    def extract_headers(self, text: str) -> Dict[str, List[str]]:
        headers: Dict[str, List[str]] = {}
        header_regex = re.compile(r"(^|\n)(#{1,6})\s+(.*)", re.MULTILINE)

        for match in header_regex.finditer(text):
            level = len(match.group(2))
            content = match.group(3).strip()
            key = f"h{level}"
            headers.setdefault(key, []).append(content)

        return headers

    def update_current_headers(
        self, current: Dict[str, List[str]], extracted: Dict[str, List[str]]
    ) -> None:
        for level in range(1, 7):
            key = f"h{level}"
            if key in extracted:
                current[key] = extracted[key]
                self.clear_lower_headers(current, level)

    def clear_lower_headers(self, headers: Dict[str, List[str]], level: int) -> None:
        for lvl in range(level + 1, 7):
            headers.pop(f"h{lvl}", None)

    def extract_urls_and_images(self, text: str) -> Tuple[str, List[str], List[str]]:
        urls: List[str] = []
        images: List[str] = []
        url_index = 0
        image_index = 0

        def replace_image(match: re.Match[str]) -> str:
            alt_text, url = match.groups()
            images.append(url)
            return f"![{alt_text}]({{$img{image_index}}})"

        def replace_url(match: re.Match[str]) -> str:
            nonlocal url_index
            link_text, url = match.groups()
            urls.append(url)
            result = f"[{link_text}]({{$url{url_index}}})"
            url_index += 1
            return result

        content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, text)
        content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_url, content)

        return content, urls, images
