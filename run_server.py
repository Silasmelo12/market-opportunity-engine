"""
Single entrypoint for Market Opportunity & Bottom Statistical Engine Web Terminal.
Starts Uvicorn server hosting both the FastAPI backend and HTML5 Web Terminal.
"""

import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

def main():
    print("==================================================================")
    print(" MARKET OPPORTUNITY & BOTTOM STATISTICAL ENGINE - FASTAPI + SPA")
    print(" Servidor rodando em: http://127.0.0.1:8000")
    print(" Terminal Web 60fps com TradingView & Filtros Instantâneos 0ms")
    print("==================================================================")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
