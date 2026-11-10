#!/usr/bin/env bash
cd /workspace/Project-Dystopia-Core || exit 1
PY=/usr/local/bin/python3
rc=0
echo "== ノード =="; $PY scripts/audit_nodes.py || rc=1
echo "== ローカルモデル =="; $PY scripts/audit_models.py || rc=1
echo "== URL =="; $PY scripts/audit_urls.py || rc=1
echo "== 結果: $([ $rc -eq 0 ] && echo 合格 || echo 要修正) =="
exit $rc
