# Simulator

For the MVP, incidents are simulated directly from backend endpoints:

```bash
curl -X POST http://localhost:8000/simulate/memory-leak
curl -X POST http://localhost:8000/simulate/cpu-spike
```

Later this folder can contain Docker Compose microservices and fault injection scripts.
