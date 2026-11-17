import pathlib

p_html = pathlib.Path("src/web/index.html")
c_html = p_html.read_text(encoding="utf-8")
old_div = """          <div id="chart-proventos-detailed" class="relative block h-72 w-full mt-4 text-slate-400 text-sm">
            Carregando proventos...
          </div>"""
new_div = """          <div id="chart-proventos-detailed" class="w-full h-72 mt-2 relative overflow-hidden block"></div>"""
assert old_div in c_html, "old_div not found in index.html"
c_html = c_html.replace(old_div, new_div, 1)
p_html.write_text(c_html, encoding="utf-8")
print("Updated index.html")

p_app = pathlib.Path("src/web/app.js")
c_app = p_app.read_text(encoding="utf-8")

old_plotly = "  Plotly.react(container, [trace], layout, { responsive: true, displayModeBar: false });"
new_plotly = """  container.innerHTML = '';
  Plotly.react(container, [trace], layout, { responsive: true, displayModeBar: false });"""
assert old_plotly in c_app, "old_plotly not found in app.js"
c_app = c_app.replace(old_plotly, new_plotly, 1)
p_app.write_text(c_app, encoding="utf-8")
print("Updated app.js")
