#!/bin/bash

# Run a temporary Docker container with the same volume mount to delete the files
docker run --rm -v $(pwd)/../data/web:/cleanup alpine sh -c "
  rm -rf /cleanup/authservice/migrations /cleanup/authservice/__pycache__
  rm -rf /cleanup/backend/migrations /cleanup/backend/__pycache__
  rm -rf /cleanup/dashboard/migrations /cleanup/dashboard/__pycache__
  rm -rf /cleanup/pong/migrations /cleanup/pong/__pycache__
  rm -rf /cleanup/tournaments/migrations /cleanup/tournaments/__pycache__
  rm -rf /cleanup/runtime/__pycache__
"
