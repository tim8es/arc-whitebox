from methods.e050_float64_v29 import git_blob_sha, mechanical_float64_source


def test_git_blob_sha_matches_git_object_format():
    assert git_blob_sha("test content\n") == "d670460b4b4aece5915caf5c68d12f560a9fe3e4"


def test_float64_transform_is_only_dtype_token_substitution():
    src = "a=fnp.float32\nb=fnp.float32\nx=1.23456789\n# no rescue\n"
    out, count = mechanical_float64_source(src)
    assert count == 2
    assert out == "a=fnp.float64\nb=fnp.float64\nx=1.23456789\n# no rescue\n"


def test_transform_does_not_invent_stabilization():
    src = "dtype=fnp.float32\nvalue = x @ y\n"
    out, _ = mechanical_float64_source(src)
    lowered = out.lower()
    for token in ("jitter", "psd repair", "fallback", "damping", "shrinkage", "pinv"):
        assert token not in lowered
