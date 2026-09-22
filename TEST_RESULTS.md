# TEST RESULTS

## Latest Test Run: [2026-09-22]
- **Target**: `smoke_test.py` & `engine/test_getdeploying_parser.py`
- **Environment**: Windows Host / Python 3.14 (pwsh)
- **Status**: ✅ PASS
- **Details**: 
  - `smoke_test.py`: `PASS: 11 history entries, 8 GPU stats verified with YTD column.`
  - `engine/test_getdeploying_parser.py`: `Ran 5 tests in 0.002s, OK` (stat card, schema FAQ, narrative text, table formats).
  - Production Pipeline & SFTP Deployment: ✅ PASS (`bmwseals.com/gpus`).

---

## Historical Results
| Date | Test | Result | Notes |
|------|------|--------|-------|
| 2026-09-22 | `smoke_test.py` | ✅ PASS | Post-GB200 calibration & MI300X integration (8 core models). |
| 2026-09-22 | `engine/test_getdeploying_parser.py` | ✅ PASS | Validated 4-layer DOM extraction against 2026 GetDeploying UI. |
| 2026-09-22 | `engine/backfill_bridge.py` | ✅ PASS | Bridged Aug 15 – Sept 22 (18 dates, 414 records + MI300X history). |
| 2026-05-22 | `smoke_test.py` | ✅ PASS | Post-Stealth & Venv Parity updates. |
| 2026-05-17 | `smoke_test.py` | ✅ PASS | Post-Mobile Grid & Responsive Sync Indicators. |
| 2026-05-17 | `smoke_test.py` | ✅ PASS | Post-Outlier Shield & UI Calibrations. |
| 2026-05-17 | `smoke_test.py` | ✅ PASS | Post-Label & Date Calibration. |
| 2026-05-15 | `smoke_test.py` | ✅ PASS | Post-Reliability refactor. |
| 2026-05-15 | `engine/index_scraper.py` | ❌ FAIL | Path error in venv (fixed by shell wrapper). |
| 2026-05-10 | `test_gpus.sh` | ✅ PASS | Initial V4.2.1 validation. |

