from pydantic import BaseModel


class FileContent(BaseModel):
    path: str
    content: str
    truncated: bool
    total_lines: int
    returned_lines: int


class DirectoryEntry(BaseModel):
    name: str
    path: str
    type: str


class DirectoryListing(BaseModel):
    path: str
    entries: list[DirectoryEntry]

class SearchMatch(BaseModel):
    path: str
    line_number: int
    line: str


class SearchResult(BaseModel):
    query: str
    matches: list[SearchMatch]
    truncated: bool