from wordstat import get_word_counts


def test_normal_text():
    text = "Python is great. Python is powerful."

    result = get_word_counts(text)

    assert result["python"] == 2
    assert result["is"] == 2
    assert result["great"] == 1
    assert result["powerful"] == 1


def test_empty_text():
    text = ""

    result = get_word_counts(text)

    assert result == {}


def test_unicode_text():
    text = "hello नमस्ते café hello"

    result = get_word_counts(text)

    assert result["hello"] == 2
    assert result["नमस्ते"] == 1
    assert result["café"] == 1


def test_very_long_text():
    text = "python " * 10000

    result = get_word_counts(text)

    assert result["python"] == 10000
    assert len(result) == 1


def test_missing_file():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "wordstat.py", "missing.txt"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Error: file not found" in result.stdout


def test_case_insensitive():
    text = "Python PYTHON python Java JAVA"

    result = get_word_counts(text)

    assert result["python"] == 3
    assert result["java"] == 2
    assert len(result) == 2


def test_top_n_limit():
    text = "python python python java java react"

    result = get_word_counts(text)

    top_words = result.most_common(2)

    assert len(top_words) == 2
    assert top_words[0] == ("python", 3)
    assert top_words[1] == ("java", 2)


def test_invalid_n_value():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "wordstat.py", "sample.txt", "-n", "0"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "N must be greater than zero" in result.stderr
