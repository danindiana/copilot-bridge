# Request Flow Sequence Diagram

This diagram shows the detailed flow of a request through copilot-bridge with dual-GPU smart routing.

```mermaid
sequenceDiagram
    participant Client as GitHub Copilot<br/>Client
    participant Proxy as Proxy Server<br/>(Port 5000)
    participant Router as Smart Router
    participant Classifier as Task Classifier
    participant Orchestrator as Dual-GPU<br/>Orchestrator
    participant Ollama as Ollama Server<br/>(localhost:11434)
    participant GPU as GPU (0 or 1)
    participant Metrics as Prometheus<br/>Metrics

    %% Request initiation
    Client->>Proxy: POST /v1/chat/completions
    Note over Client,Proxy: HTTP Request with prompt
    
    %% Request validation
    Proxy->>Proxy: Validate request
    Proxy->>Metrics: Increment request_total
    
    %% Environment check
    Proxy->>Proxy: Check ENABLE_DUAL_GPU
    
    alt Dual-GPU Enabled
        Proxy->>Router: Forward request
        Note over Router: Dual-GPU Mode Active
        
        %% Task classification
        Router->>Classifier: classify_task(prompt)
        Classifier->>Classifier: Analyze keywords
        
        alt Contains SIMPLE keywords
            Classifier-->>Router: TaskComplexity.SIMPLE
            Note over Classifier: Keywords: "autocomplete",<br/>"format", "lint"
        else Contains MODERATE keywords
            Classifier-->>Router: TaskComplexity.MODERATE
            Note over Classifier: Keywords: "refactor",<br/>"debug", "explain"
        else Contains COMPLEX keywords
            Classifier-->>Router: TaskComplexity.COMPLEX
            Note over Classifier: Keywords: "design",<br/>"implement", "algorithm"
        end
        
        %% Model selection
        Router->>Orchestrator: select_gpu_and_model(complexity)
        
        alt SIMPLE Task
            Orchestrator-->>Router: GPU 0, qwen2.5-coder:1.5b
            Note over Orchestrator: Fast model<br/>0.34s response time
        else MODERATE/COMPLEX Task
            Orchestrator-->>Router: GPU 0, qwen2.5-coder:7b
            Note over Orchestrator: Quality model<br/>~19s response time
        end
        
        %% Ollama request
        Router->>Ollama: POST /api/generate
        Note over Router,Ollama: Selected model + prompt
        Ollama->>GPU: Load model on GPU
        GPU->>GPU: Execute inference
        GPU-->>Ollama: Generated response
        Ollama-->>Router: JSON response
        
        %% Response processing
        Router->>Router: Format response
        Router->>Metrics: Record latency
        Router->>Metrics: Update model_used counter
        Router-->>Proxy: Response with metadata
        
    else Dual-GPU Disabled
        Proxy->>Ollama: Direct API call
        Note over Proxy: Fallback to single model
        Ollama->>GPU: Execute on GPU 0
        GPU-->>Ollama: Response
        Ollama-->>Proxy: Response
    end
    
    %% Error handling
    alt Request Timeout
        Router->>Router: Detect timeout (180s)
        Router->>Metrics: Increment error_count
        Router-->>Proxy: Error response
        Proxy->>Ollama: Retry with fallback
        Ollama-->>Proxy: Response
    end
    
    %% Logging and metrics
    Proxy->>Metrics: Record response_time
    Proxy->>Metrics: Update task_complexity_count
    Proxy->>Proxy: Log to JSON
    
    %% Return to client
    Proxy-->>Client: HTTP 200 + response
    Note over Client,Proxy: Streaming or complete

    %% Metrics collection
    Note over Metrics: Continuous monitoring:<br/>- Request rate<br/>- Latency percentiles<br/>- Model usage<br/>- Error rates
```

## Flow Description:

### 1. Request Initiation (Steps 1-3)
- Client sends HTTP POST to `/v1/chat/completions`
- Proxy validates request structure
- Metrics counter incremented

### 2. Environment Check (Step 4)
- Check `ENABLE_DUAL_GPU` environment variable
- Determines routing strategy (dual-GPU vs single-model)

### 3. Task Classification (Steps 5-8)
**SIMPLE Task Detection:**
- Keywords: `autocomplete`, `complete`, `format`, `lint`, `syntax`
- Model: qwen2.5-coder:1.5b (1GB VRAM)
- Response time: ~0.34s

**MODERATE Task Detection:**
- Keywords: `refactor`, `debug`, `explain`, `test`, `document`
- Model: qwen2.5-coder:7b (8GB VRAM)
- Response time: ~19s

**COMPLEX Task Detection:**
- Keywords: `design`, `implement`, `algorithm`, `architect`, `system`
- Model: qwen2.5-coder:7b (8GB VRAM)
- Response time: ~19s

### 4. Model Selection (Steps 9-10)
- Orchestrator selects optimal GPU and model
- Considers task complexity and resource availability
- Returns configuration to router

### 5. Ollama Execution (Steps 11-15)
- Router sends request to Ollama endpoint
- Ollama loads model on selected GPU
- GPU executes inference
- Response returned through stack

### 6. Error Handling (Steps 16-19)
- Timeout detection (180 second threshold)
- Automatic retry with fallback model
- Error metrics recorded
- Graceful degradation

### 7. Metrics & Logging (Steps 20-22)
**Prometheus Metrics:**
- `copilot_bridge_requests_total{complexity="SIMPLE|MODERATE|COMPLEX"}`
- `copilot_bridge_response_time_seconds{model="1.5b|7b"}`
- `copilot_bridge_model_used_total{model="1.5b|7b"}`
- `copilot_bridge_errors_total{type="timeout|connection"}`

**JSON Logging:**
```json
{
  "timestamp": "2025-10-19T12:34:56Z",
  "prompt": "format this code",
  "complexity": "SIMPLE",
  "model": "qwen2.5-coder:1.5b",
  "gpu": "GPU_0",
  "response_time_ms": 340,
  "tokens_generated": 75
}
```

### 8. Response Return (Step 23)
- HTTP 200 with generated response
- Supports streaming or complete responses
- Includes model metadata in headers

## Performance Optimization:

### Fast Path (SIMPLE Tasks)
- **Before:** 19s with 7B model
- **After:** 0.34s with 1.5B model
- **Speedup:** 55.9x faster
- **Memory:** 87% reduction (1GB vs 8GB)

### Quality Path (MODERATE/COMPLEX Tasks)
- Maintains 7B model quality
- No degradation in output
- Appropriate for complex reasoning

## Error Recovery:

1. **Primary Request Fails**
   - Automatic retry with same model
   - Up to 3 retry attempts

2. **Timeout Exceeded**
   - Switch to fallback model
   - Log timeout event
   - Update metrics

3. **GPU Unavailable**
   - Fallback to CPU inference
   - Notify via metrics
   - Continue operation

## Monitoring Points:

- **Request Rate:** Requests per second by complexity
- **Latency:** P50, P95, P99 response times
- **Model Usage:** Distribution of 1.5B vs 7B usage
- **Error Rate:** Percentage of failed requests
- **GPU Utilization:** Memory and compute usage
