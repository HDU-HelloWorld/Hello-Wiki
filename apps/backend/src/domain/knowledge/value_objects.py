from enum import StrEnum


class PageStatus(StrEnum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    MERGED = "merged"


class ChunkStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"


class EventType(StrEnum):
    CREATION = "creation"
    UPDATE = "update"
    MERGE = "merge"
    OBSERVATION = "observation"
    SOURCE_ADDED = "source_added"
