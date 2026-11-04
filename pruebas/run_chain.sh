#!/bin/bash
# uso: run_chain.sh <notebook_run> <dir_salida> <tag>
cd /root/dungeon-master-agentic
for i in 1 2 3; do
  SECUENCIA=${SEQ:-holdout} RUN_TAG=_$3$i /opt/venv-ragas/bin/jupyter nbconvert --to notebook --execute \
    --ExecutePreprocessor.timeout=5400 --ExecutePreprocessor.kernel_name=python3 $1 --output $2/v2_run$i.ipynb > $2/v2_run$i.log 2>&1
  echo "$3 run$i exit=$?"
  mv -f juez_por_turno_$3$i.csv faithfulness_$3$i.csv respuestas_$3$i.json dialogo_$3$i.csv $2/ 2>/dev/null
done
