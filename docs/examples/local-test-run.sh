#!/bin/bash

# Essential Test Commands
echo "🧪 Quick Test Commands:"

echo "🐍 Python Services:"
echo "  cd services && ./build.sh --test-only"

echo "🚪 Gateway:"
echo "  cd gateway && ./build.sh --test-only"

echo "⚛️ Frontend:"
echo "  cd frontend && ./build.sh --test-only"

echo "🔗 Integration:"
echo "  cd integration_tests && ./run_all_tests.sh all"
