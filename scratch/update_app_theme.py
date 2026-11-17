with open('src/web/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = """  const icon = document.getElementById('theme-toggle-icon');
  const text = document.getElementById('theme-toggle-text');
  if (icon && text) {
    if (theme === 'light') {
      icon.textContent = '\u00e2\u02dc\u20ac\u00ef\u00b8\u008f';
      text.textContent = 'Claro';
    } else {
      icon.textContent = '\u00f0\u0178\u0152\u2122';
      text.textContent = 'Escuro';
    }
  }"""

replacement = """  const icon = document.getElementById('theme-toggle-icon');
  const text = document.getElementById('theme-toggle-text');
  if (icon) {
    const useEl = icon.querySelector('use');
    if (useEl) {
      useEl.setAttribute('href', theme === 'light' ? '#icon-sun' : '#icon-moon');
    } else {
      icon.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><use href="${theme === 'light' ? '#icon-sun' : '#icon-moon'}"></use></svg>`;
    }
  }
  if (text) {
    text.textContent = theme === 'light' ? 'Claro' : 'Escuro';
  }"""

if target in content:
    new_content = content.replace(target, replacement, 1)
    with open('src/web/app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully updated app.js theme toggle icon logic!')
else:
    print('Target not found in app.js!')
