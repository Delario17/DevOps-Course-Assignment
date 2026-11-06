"""Student 241250078: reject candidates that reorder required instructions."""

import pytest

from draft.autobuild import prepare_candidate


def test_241250078_reordered_required_instructions_are_rejected():
    base_image = "m.daocloud.io/docker.io/library/python:3.13-slim"
    broken = (
        f"FROM {base_image}\n"
        "WORKDIR /work\n"
        "COPY main.c Makefile ./\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )
    pinned = f"FROM {base_image}@sha256:" + "a" * 64
    candidate = (
        f"{pinned}\n"
        "COPY main.c Makefile ./\n"
        "WORKDIR /work\n"
        "RUN apt-get update && apt-get install -y build-essential\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )

    with pytest.raises(
        ValueError,
        match="Candidate changed required project/build/runtime instructions",
    ):
        prepare_candidate(broken, candidate)
