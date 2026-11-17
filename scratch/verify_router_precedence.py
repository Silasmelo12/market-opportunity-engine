import sys
sys.path.insert(0, '.')
import time
import uvicorn
import threading
from playwright.sync_api import sync_playwright
from src.api.server import app

PORT = 58777
config = uvicorn.Config(app, host='127.0.0.1', port=PORT, log_level='error')
server = uvicorn.Server(config)
t = threading.Thread(target=server.run, daemon=True)
t.start()
time.sleep(1.5)

base_url = f'http://127.0.0.1:{PORT}'

def active_pane_id(page):
    return page.evaluate('''() => {
        const visible = [...document.querySelectorAll('.tab-view, .tab-pane')].filter(el => !el.classList.contains('hidden'));
        return visible.map(el => el.id);
    }''')

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()

    # Caso 1: Conflito entre Hash e mo_active_route -> Hash prevalece
    page.goto(f'{base_url}/?e2e=1#quant/radar')
    page.evaluate('''() => {
        localStorage.setItem('mo_active_route', 'carteira/posicoes');
        localStorage.setItem('mo_active_tab', 'posicoes');
    }''')
    page.goto(f'{base_url}/?e2e=1#quant/radar')
    page.wait_for_selector('#tab-pane-radar', state='visible')
    panes = active_pane_id(page)
    assert 'tab-pane-radar' in panes, f'Hash #quant/radar deveria prevalecer sobre mo_active_route, panes visíveis: {panes}'
    print('Caso 1 Aprovado: Hash explícito prevalece sobre mo_active_route.')

    # Caso 2: Sem hash na URL -> mo_active_route prevalece sobre mo_active_tab antigo
    page.evaluate('''() => {
        history.replaceState(null, '', '/?e2e=1');
        localStorage.setItem('mo_active_route', 'quant/simulador');
        localStorage.setItem('mo_active_tab', 'resumo');
    }''')
    page.reload(wait_until='load')
    page.wait_for_selector('#tab-simulator', state='visible')
    panes = active_pane_id(page)
    assert 'tab-simulator' in panes, f'mo_active_route deveria prevalecer, panes visíveis: {panes}'
    print('Caso 2 Aprovado: mo_active_route prevalece sobre mo_active_tab em recarga sem hash.')

    # Caso 3: Fallback legado -> se mo_active_route estiver ausente, mo_active_tab é honrado
    page.evaluate('''() => {
        history.replaceState(null, '', '/?e2e=1');
        localStorage.removeItem('mo_active_route');
        localStorage.setItem('mo_active_tab', 'proventos');
    }''')
    page.reload(wait_until='load')
    page.wait_for_selector('#tab-pane-proventos', state='visible')
    panes = active_pane_id(page)
    assert 'tab-pane-proventos' in panes, f'Fallback legado mo_active_tab deveria abrir proventos, panes visíveis: {panes}'
    print('Caso 3 Aprovado: Fallback legado mo_active_tab honrado quando mo_active_route ausente.')

    # Caso 4: Hash desconhecido/inválido -> fallback seguro para Visão Geral
    page.goto(f'{base_url}/?e2e=1#rota-inexistente/xyz')
    page.wait_for_selector('#tab-overview', state='visible')
    panes = active_pane_id(page)
    assert 'tab-overview' in panes, f'Rota desconhecida deveria fazer fallback para Visão Geral, panes visíveis: {panes}'
    print('Caso 4 Aprovado: Rota desconhecida redireciona com segurança para Visão Geral.')

    b.close()

server.should_exit = True
print('Todos os 4 cenários de roteamento foram validados com 100% de sucesso!')
