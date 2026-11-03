import pytest

from draft.autobuild import prepare_candidate


def test_zyl_rejects_multiple_from_in_candidate():
    base = (
        "FROM python:3.13-slim\n"
        "WORKDIR /work\n"
        "COPY main.c Makefile ./\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )

    pinned = "FROM python:3.13-slim@sha256:" + "a" * 64

    candidate = base.replace(
        "FROM python:3.13-slim", pinned
    ).replace(
        "RUN make\n",
        "RUN apt-get update && apt-get install -y build-essential\n"
        "RUN make\n",
    )

    candidate += "\nFROM ubuntu:24.04\n"

    with pytest.raises(
        ValueError,
        match="Only single-stage candidates are supported",
    ):
        prepare_candidate(base, candidate)
