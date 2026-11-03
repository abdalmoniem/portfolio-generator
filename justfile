set export := true

alias s := sync
alias g := generate
alias w := watch

export TARGET_OS := os()

[doc('List available recipes')]
default:
    @just --list --unsorted

[doc('Sync and install uv deps')]
[group('build')]
[script]
sync:
    if [ "$TARGET_OS" = "android" ]; then
        uv cache clean
        TORNADO_EXTENSION=0 uv sync || true
        _PYTHON_HOST_PLATFORM=android_24_arm64_v8a TORNADO_EXTENSION=0 uv sync
    else
        uv sync
    fi

[doc('Generate the HTML and PDF files')]
[group('build')]
generate: sync
    @uv run scripts/generate_portfolio.py
    @just post_generate

[doc('Start a livereload server to watch changes')]
[group('build')]
watch: sync
    @uv run scripts/watch.py

[private]
[script]
post_generate:
    html_files="generated/*.html"

    echo

    if command -v ccze >/dev/null 2>&1; then
        just file_info "$html_files" | ccze --raw-ansi
        just du_info   "$html_files" | ccze --raw-ansi
    else
        just file_info "$html_files"
        just du_info   "$html_files"
    fi

[private]
file_info files:
    @file $files

[private]
du_info files:
    @du -hs --time --time-style=+'%a, %d/%b/%Y - %r' $files
