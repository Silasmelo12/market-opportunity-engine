import pathlib

p = pathlib.Path("tests/e2e/test_proventos_layout.py")
content = p.read_text(encoding="utf-8")

old_snippet = """        page.evaluate(
            \"\"\"(payload) => {
                history.replaceState(null, '', '/' + location.search);
                localStorage.setItem('mo_active_tab', 'proventos');
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload));
            }\"\"\",
            payload,
        )"""

new_snippet = """        page.evaluate(
            \"\"\"(payload) => {
                history.replaceState(null, '', '/' + location.search);
                localStorage.removeItem('mo_active_route');
                localStorage.setItem('mo_active_tab', 'proventos');
                localStorage.setItem('market_engine_portfolio_v1', JSON.stringify(payload));
            }\"\"\",
            payload,
        )"""

assert old_snippet in content, "old_snippet not found in test_proventos_layout.py"
p.write_text(content.replace(old_snippet, new_snippet, 1), encoding="utf-8")
print("Successfully updated tests/e2e/test_proventos_layout.py")
