# Graph Report - Market Opportunity & Bottom Statistical Engine  (2026-10-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1667 nodes · 4697 edges · 60 communities (56 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 287 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `358f292d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- OHLCVSeries
- resumeSession
- b3_parser.py
- server.py
- el
- numpy
- modern-screenshot.umd.js
- test_dashboard_navigation.py
- showToast
- actOnAgentTarget
- connectSSE
- evaluator/__init__.py
- QuantitativeIndicatorsEngine
- app.py
- renderDesignVisual
- pandas
- ProprietaryReversalEngine
- live-browser.js
- StrategyCatalog
- mountSvelteComponentVariant
- app.js
- SignalRecord
- extension
- steps
- initGlobalBar
- common.ps1
- handleManualEditActivity
- createLiveBrowserDomHelpers
- createLiveBrowserSessionState
- captureElementToBlob
- resolveLiveInjectionAnchor
- test_ui_contracts.py
- conftest.py
- sync-config.template.yml
- test_api_endpoints.py
- focusSteerChat
- loadRadarData
- setupPortfolioTab
- services
- after_implement
- steps
- normalizeManualContextText
- applyEditing
- DailyCache
- loadAnalysisData
- syncEditBadgeHitProxies
- run_server.py
- classify_timing_status
- navigateToRoute
- renderOverviewDashboard
- stripCorporateSuffix
- live-browser-ignores.js
- walk
- documentRefSegment
- scopeCssBlock
- interface
- enableInlineEdit
- showShaderOverlay

## God Nodes (most connected - your core abstractions)
1. `OHLCVSeries` - 104 edges
2. `SignalRecord` - 83 edges
3. `ClassicStrategiesEngine` - 39 edges
4. `connectSSE()` - 34 edges
5. `resumeSession()` - 33 edges
6. `setLiveState()` - 33 edges
7. `QuantitativeIndicatorsEngine` - 32 edges
8. `showToast()` - 31 edges
9. `initGlobalBar()` - 30 edges
10. `el()` - 29 edges

## Surprising Connections (you probably didn't know these)
- `_slice_series()` --calls--> `OHLCVSeries`  [EXTRACTED]
  tests/unit/test_portfolio_simulator.py → src/strategies/base.py
- `_sig_key()` --uses--> `SignalRecord`  [INFERRED]
  tests/unit/test_anti_lookahead.py → src/strategies/base.py
- `test_asset_names_and_radar_items()` --calls--> `get_asset_name()`  [EXTRACTED]
  tests/unit/test_api_endpoints.py → src/ui/theme.py
- `create_valid_reversal_double_bottom()` --uses--> `OHLCVSeries`  [INFERRED]
  tests/fixtures_double_patterns.py → src/strategies/base.py
- `create_valid_reversal_double_top()` --uses--> `OHLCVSeries`  [INFERRED]
  tests/fixtures_double_patterns.py → src/strategies/base.py

## Import Cycles
- None detected.

## Communities (60 total, 4 thin omitted)

### Community 0 - "OHLCVSeries"
Cohesion: 0.06
Nodes (16): OHLCVSeries, ClassicStrategiesEngine, compute_rsi(), _detect_double_bottom_raw(), _detect_double_top_raw(), DoublePatternParams, _rolling_max_prev(), _rolling_min_prev() (+8 more)

### Community 1 - "resumeSession"
Cohesion: 0.07
Nodes (76): applyParamDefaults(), applyParamValue(), applyPlaceholderDimensions(), applySavedSessionMeta(), buildParamsPanel(), clampVariantIndex(), clearHandled(), closedClipPath() (+68 more)

### Community 2 - "b3_parser.py"
Cohesion: 0.07
Nodes (37): B3Holding, B3MonthlyIncome, B3ParseResult, B3TimelinePoint, b3_parse_uploaded_file(), _build_holdings_from_events(), _build_timeline_from_events(), _classify_asset() (+29 more)

### Community 3 - "server.py"
Cohesion: 0.08
Nodes (47): AccumulationPoint, AnalyzeResponse, AssetOpportunityProfileModel, B3MovementRecord, BuyEntrySchema, CandleBar, OptimizeCombinationsRequest, OptimizeCombinationsResponse (+39 more)

### Community 4 - "el"
Cohesion: 0.06
Nodes (65): actionLabel(), applyConfigureBarChrome(), bindConfigureCountPillTooltip(), bindConfigureInlineControlHover(), bindConfigureModifierPillHover(), buildConfigureActionControl(), buildConfigureCountControl(), buildConfigureRow() (+57 more)

### Community 5 - "numpy"
Cohesion: 0.07
Nodes (21): evaluate_strategy_performance(), split_closed_and_open_signals(), ReferenceLineSegment, StrategyStatsSummary, MQL5CandleEngine, compute_atr(), compute_rsi_series(), generate_synthetic_market_series() (+13 more)

### Community 6 - "modern-screenshot.umd.js"
Cohesion: 0.09
Nodes (55): ae(), be(), bt(), Ce(), s(), Ct(), de(), dt() (+47 more)

### Community 7 - "test_dashboard_navigation.py"
Cohesion: 0.05
Nodes (25): app_page(), quote_handler(), _hash(), _history_page(), test_contextual_return_deep_link_is_safe_without_history_back(), test_contextual_return_internal_flow_history(), test_dashboard_math_is_internally_coherent(), test_fourth_kpi_excludes_missing_quotes_from_denominator() (+17 more)

### Community 8 - "showToast"
Cohesion: 0.08
Nodes (52): abandonForeignSession(), abandonSupersededGo(), armPageChatForTyping(), buildSteerProcessingDots(), buildSteerQueueHint(), clearSteerAwaitTimer(), collapsePageChat(), copyToClipboard() (+44 more)

### Community 9 - "actOnAgentTarget"
Cohesion: 0.06
Nodes (52): actOnAgentTarget(), agentTargetBusyReason(), agentTargetOverlayGone(), agentTargetTaken(), beginEditPin(), buildAnnotationsForCapture(), buildPinElement(), cancelEditingPin() (+44 more)

### Community 10 - "connectSSE"
Cohesion: 0.13
Nodes (51): abortSvelteComponentInjection(), beginNewLiveConfiguration(), cancelEditing(), cancelEditingToPicking(), cancelInsertConfigure(), cleanup(), cleanupAcceptedSession(), clearAnnotations() (+43 more)

### Community 11 - "evaluator/__init__.py"
Cohesion: 0.09
Nodes (24): optimize_combinations_endpoint(), BuyEntryRecord, CycleSimulationResult, optimize_dca_strategies(), optimize_strategy_pairs(), StrategyPairRankItem, TradeRecord, advise_portfolio_rebalance() (+16 more)

### Community 12 - "QuantitativeIndicatorsEngine"
Cohesion: 0.10
Nodes (18): compute_rolling_std(), compute_sma(), convert_signals_to_records(), QuantitativeIndicatorsEngine, render_price_chart_lightweight(), make_synthetic_ohlcv(), test_bollinger_close_in_signals(), test_engine_initialization() (+10 more)

### Community 13 - "app.py"
Cohesion: 0.10
Nodes (11): get_cached_asset_data(), main(), simulate_accumulation(), SimulationResult, render_guide_tab(), render_sidebar(), render_simulator_fragment(), render_state_monitor() (+3 more)

### Community 14 - "renderDesignVisual"
Cohesion: 0.08
Nodes (39): buildCollapsible(), buildColorModels(), buildDesignHeader(), buildListHtml(), buildRadiiModels(), buildTypographyModels(), cssSafe(), designEmptyMessage() (+31 more)

### Community 15 - "pandas"
Cohesion: 0.09
Nodes (11): DataLoader, clean_and_normalize_df(), resample_ohlcv(), compute_ema(), _format_date(), render_main_chart(), render_price_chart_plotly(), test_clean_and_normalize_intraday_window() (+3 more)

### Community 16 - "ProprietaryReversalEngine"
Cohesion: 0.10
Nodes (12): ProprietaryReversalEngine, make_series(), test_four_variants_independence_and_current_state(), test_retest_expiration_after_m_bars_without_touch(), test_retest_gap_down_executes_at_open(), test_retest_single_cycle_first_touch_only(), test_retest_touch_and_close_below_still_executes_at_line(), test_successive_breakouts_overwrite_reference_line() (+4 more)

### Community 17 - "live-browser.js"
Cohesion: 0.07
Nodes (32): applyGlobalBarLabelState(), applyLiveBarPreference(), applyPlaceholderSizingStyles(), buildPlaceholderResizeHandles(), checkpointPayload(), commitAcceptedVariantToDom(), createInsertPlaceholder(), cursorForPlaceholderEdge() (+24 more)

### Community 18 - "StrategyCatalog"
Cohesion: 0.08
Nodes (14): _get_cache(), _load_and_profile_single_asset(), _prewarm_featured_radar(), _worker(), _scan_single_ticker(), _set_cache(), _parse_period_days(), strip_corporate_suffix() (+6 more)

### Community 19 - "mountSvelteComponentVariant"
Cohesion: 0.09
Nodes (34): acceptedDomAlreadyClean(), applyOriginalAttrsToSvelteAnchor(), clearHandledWrapperReloadStamp(), clearMountErrorCard(), commitAcceptedSvelteComponentToDom(), componentModuleCandidates(), cyclingCounterText(), cyclingShownVariant() (+26 more)

### Community 20 - "app.js"
Cohesion: 0.09
Nodes (31): ALLOWED_RETURN_ROUTES, applyClientSideFiltering(), applyTheme(), ASSET_NAMES, CANONICAL_ROUTES, determineActiveRoute(), elements, formatPrice() (+23 more)

### Community 21 - "SignalRecord"
Cohesion: 0.13
Nodes (18): simulate_cycle_trade(), SignalRecord, make_test_series(), test_optimize_dca_strategies_finds_champion(), test_optimize_strategy_pairs_finds_champion(), test_simulate_accumulation_date_range_filter(), test_simulate_accumulation_fixed_contributions(), test_simulate_cycle_trade_buy_sell_pairing() (+10 more)

### Community 22 - "extension"
Cohesion: 0.06
Nodes (30): command, optional, prompt, aliases, description, file, name, description (+22 more)

### Community 23 - "steps"
Cohesion: 0.06
Nodes (30): args, inputs, integration, spec, default, prompt, type, any (+22 more)

### Community 24 - "initGlobalBar"
Cohesion: 0.11
Nodes (27): agentHasWorkInFlight(), agentStatusText(), barPaletteForTheme(), brandMarkSvg(), designPanelCss(), detectPageTheme(), ensureAgentPollTooltip(), ensureSpinKeyframes() (+19 more)

### Community 25 - "common.ps1"
Cohesion: 0.16
Nodes (19): Find-SpecifyRoot(), Format-SpecKitCommand(), Get-CurrentBranch(), Get-FeaturePathsEnv(), Get-InvokeSeparator(), Get-NormalizedPriority(), Get-Python3Command(), Get-RepoRoot() (+11 more)

### Community 26 - "handleManualEditActivity"
Cohesion: 0.19
Nodes (24): clearStoredManualApplyState(), fetchPendingCount(), handleManualEditActivity(), hidePendingApplyDock(), manualApplyLoadingText(), manualApplyStateKey(), manualEditEventForCurrentPage(), numberOrNull() (+16 more)

### Community 27 - "createLiveBrowserDomHelpers"
Cohesion: 0.13
Nodes (19): createLiveBrowserDomHelpers(), activeElementDeep(), cloneWithoutChrome(), copyTextViaSelection(), cssId(), liveUiRoot(), makeFrozenAnchor(), own() (+11 more)

### Community 28 - "createLiveBrowserSessionState"
Cohesion: 0.19
Nodes (17): createLiveBrowserSessionState(), clearHandled(), clearScrollY(), clearSession(), isHandled(), loadSession(), markHandled(), nextCheckpointRevision() (+9 more)

### Community 29 - "captureElementToBlob"
Cohesion: 0.14
Nodes (19): averageRgb01(), bufferToBase64(), captureChromeNodes(), captureElementFromRenderedAncestor(), captureElementToBlob(), collectFontCssText(), cssColorToRgb01(), dominantRgb01() (+11 more)

### Community 30 - "resolveLiveInjectionAnchor"
Cohesion: 0.16
Nodes (19): buildSvelteExpressionTextMap(), buildSveltePropValuesFromLiveElement(), buildSveltePropValuesV2(), cloneWithoutElements(), collectTextNodes(), collectVisibleTexts(), cssEscapeIdent(), elementMatchesOriginalMarkup() (+11 more)

### Community 31 - "test_ui_contracts.py"
Cohesion: 0.11
Nodes (9): test_api_health_contract(), test_api_portfolio_quotes_contract(), test_api_strategies_contract(), test_regression_chart_container_no_flex_and_no_duplicate_overview(), test_spa_has_investidor10_category_accordions(), test_spa_has_investidor10_hero_kpis_and_charts(), test_spa_has_investidor10_proventos_tab(), test_spa_has_investidor10_subnav_and_tab_panes() (+1 more)

### Community 32 - "conftest.py"
Cohesion: 0.17
Nodes (4): _get_radar_disk_cache(), _set_radar_disk_cache(), _free_port(), server_url()

### Community 33 - "sync-config.template.yml"
Cohesion: 0.11
Nodes (17): analysis, design_doc_patterns, ignore_patterns, include_design_docs, output, artifacts_dir, history_limit, keep_history (+9 more)

### Community 35 - "focusSteerChat"
Cohesion: 0.20
Nodes (16): attachSteerFocusDebug(), attachSteerFocusGuard(), clearSteerFocusRecoverTimer(), focusConfigureInput(), focusSteerChat(), isInlineEditActive(), isPageEditableActive(), isPageEditableElement() (+8 more)

### Community 36 - "loadRadarData"
Cohesion: 0.17
Nodes (15): getAssetName(), loadRadarData(), renderRadarStratMenu(), renderRadarTable(), setupDirectionSelector(), setupRadarCategoryPills(), setupRadarStrategyFilter(), setupRadarTableSorting() (+7 more)

### Community 37 - "setupPortfolioTab"
Cohesion: 0.37
Nodes (15): applyB3ParsedResult(), applyRecommendedPortfolioOrders(), closePreFlightOrderModal(), hideToastNotification(), importPortfolioHoldingsFromCsv(), readPortfolioInputsToState(), renderPortfolioHoldingsEditor(), runPortfolioAdviseAndSimulate() (+7 more)

### Community 38 - "services"
Cohesion: 0.14
Nodes (13): key, sync, value, services, autoDeploy, buildCommand, envVars, name (+5 more)

### Community 39 - "after_implement"
Cohesion: 0.14
Nodes (13): command, condition, description, enabled, extension, optional, priority, prompt (+5 more)

### Community 40 - "steps"
Cohesion: 0.14
Nodes (13): jobs, validate, name, branches, branches, name, run, uses (+5 more)

### Community 41 - "normalizeManualContextText"
Cohesion: 0.19
Nodes (13): canRestoreManualEditElement(), cssIdent(), directMixedTextRestoreNodes(), findManualEditRestoreElement(), mixedTextWrapRestoreHint(), nearbyEditableTextsForManualEdit(), normalizeManualContextText(), onPendingTrashClick() (+5 more)

### Community 42 - "applyEditing"
Cohesion: 0.21
Nodes (12): applyEditing(), buildLocatorForLeaf(), copyEditContainerContext(), copyEditLeafContext(), documentRefForElement(), forbiddenManualTextChars(), maybeShowFirstSaveToast(), parseSourceLoc() (+4 more)

### Community 44 - "loadAnalysisData"
Cohesion: 0.24
Nodes (12): hideLoading(), loadAnalysisData(), renderSimulationTradesTable(), renderTopCombinationsTable(), resolveTicker(), runOptimizer(), runSimulation(), setupSimulationTab() (+4 more)

### Community 45 - "syncEditBadgeHitProxies"
Cohesion: 0.27
Nodes (10): bindEditBadgeProxy(), editBadgeProxyTargets(), initEditBadge(), initEditBadgeHitProxies(), positionEditBadge(), proxyMouseEvent(), setImportantStyle(), styleEditBadgeProxy() (+2 more)

### Community 47 - "run_server.py"
Cohesion: 0.36
Nodes (3): main(), open_browser(), main()

### Community 48 - "classify_timing_status"
Cohesion: 0.25
Nodes (4): classify_timing_status(), TimingStatus, test_timing_status_classifier_bands(), test_directional_timing_classifier_sell_bands()

### Community 49 - "navigateToRoute"
Cohesion: 0.28
Nodes (9): activateInvestidor10Tab(), navigateToRoute(), openChartForHolding(), openChartFromRadar(), renderPatrimonioDetailedChart(), renderProventosTabChart(), sanitizeTickerParam(), setupNavigationTabs() (+1 more)

### Community 50 - "renderOverviewDashboard"
Cohesion: 0.25
Nodes (9): fetchPortfolioQuotes(), getUserMetas(), loadPortfolioStorage(), renderOverviewDashboard(), renderOverviewDonutChart(), renderOverviewStackedBarChart(), saveUserMetas(), setupOverviewMetasModal() (+1 more)

### Community 51 - "stripCorporateSuffix"
Cohesion: 0.22
Nodes (9): getActionBadgeHtml(), renderOverviewGroupedHoldings(), renderPortfolioAdviseSection(), renderPortfolioEquityChart(), renderPortfolioLedgerTable(), renderPortfolioOpportunityRanking(), renderPortfolioSimulationKPIs(), runPortfolioHistoricalSimulation() (+1 more)

### Community 53 - "live-browser-ignores.js"
Cohesion: 0.52
Nodes (6): globToRegex(), matchesScope(), normalizeIgnoreRule(), normalizeIgnoreValue(), pageCandidates(), resolveDetectIgnores()

### Community 54 - "walk"
Cohesion: 0.33
Nodes (6): addManualContextText(), collectManualContextPieces(), walk(), contextElementForManualEdit(), isMeaningfulManualContextPiece(), isUsefulManualEditContext()

### Community 55 - "documentRefSegment"
Cohesion: 0.40
Nodes (6): documentRefClassSuffix(), documentRefIdSuffix(), documentRefSegment(), elementMatchesManualRefSegment(), indexAmongSameTag(), normalizeDocumentRefToken()

### Community 56 - "scopeCssBlock"
Cohesion: 0.33
Nodes (6): findMatchingCssBrace(), prefixCssSelectors(), scopeCssBlock(), shouldScopeNestedCssAtRule(), splitCssSelectorList(), unwrapSvelteGlobalSelector()

### Community 57 - "interface"
Cohesion: 0.40
Nodes (4): interface, default_prompt, display_name, short_description

### Community 58 - "enableInlineEdit"
Cohesion: 0.40
Nodes (5): collectEditableTextRows(), visit(), enableInlineEdit(), onInlineInput(), wrapMixedContentTextNodes()

### Community 59 - "showShaderOverlay"
Cohesion: 0.50
Nodes (3): compileShader(), showShaderBitmapFallback(), showShaderOverlay()

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OHLCVSeries` connect `OHLCVSeries` to `numpy`, `evaluator/__init__.py`, `QuantitativeIndicatorsEngine`, `app.py`, `pandas`, `ProprietaryReversalEngine`, `StrategyCatalog`, `SignalRecord`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `OHLCVSeries` (e.g. with `DataLoader` and `optimize_dca_strategies()`) actually correct?**
  _`OHLCVSeries` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `OHLCVSeries` be split into smaller, more focused modules?**
  _Cohesion score 0.05994710549515134 - nodes in this community are weakly interconnected._
- **Why does `SignalRecord` connect `SignalRecord` to `OHLCVSeries`, `server.py`, `numpy`, `evaluator/__init__.py`, `QuantitativeIndicatorsEngine`, `app.py`, `pandas`, `ProprietaryReversalEngine`, `StrategyCatalog`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `SignalRecord` (e.g. with `optimize_dca_strategies()` and `optimize_strategy_pairs()`) actually correct?**
  _`SignalRecord` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Should `resumeSession` be split into smaller, more focused modules?**
  _Cohesion score 0.06596491228070175 - nodes in this community are weakly interconnected._
- **Should `b3_parser.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0654490106544901 - nodes in this community are weakly interconnected._