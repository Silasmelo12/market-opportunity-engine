import * as React from "react";
import { renderToString } from "react-dom/server";
import { App } from "./app/App";

export function renderAppToString(): string {
  return renderToString(<App />);
}
