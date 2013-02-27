"""Utilities for working with git refs."""

import doctest


def makeRemote(ref, remote):
    """Return a Git reference based on a local name and a remote name.

    Usage example:
        >>> makeRemote("mywork", "origin")
        'refs/remotes/origin/mywork'

        >>> makeRemote("mywork", "github")
        'refs/remotes/github/mywork'
    """
    return str("refs/remotes/" + remote + "/" + ref)


if __name__ == "__main__":
    doctest.testmod()
