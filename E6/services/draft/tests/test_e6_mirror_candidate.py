import pytest

from draft.autobuild import prepare_candidate


def test_mirror_candidate_requires_matching_baseline():
    base = "m.daocloud.io/docker.io/library/python:3.13-slim"
    pinned = base + "@sha256:" + "a" * 64

    broken = (
        f"FROM {base}\n"
        "WORKDIR /work\n"
        "COPY main.c Makefile ./\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )

    candidate = broken.replace(
        f"FROM {base}", f"FROM {pinned}"
    ).replace(
        "RUN make\n",
        "RUN apt-get update && "
        "apt-get install -y make gcc libc6-dev\n"
        "RUN make\n",
    )

    assert prepare_candidate(broken, candidate) == broken.replace(
        f"FROM {base}", f"FROM {pinned}"
    )

    mismatched = broken.replace(base, "python:3.13-slim")

    with pytest.raises(
        ValueError,
        match="Candidate changed the original base image tag",
    ):
        prepare_candidate(mismatched, candidate)
