# Notes of a web version

## Goal

Create a self-contained web version of typeout that runs purely in the browser - no backend server, no Python, just HTML/JS that can transcribe audio/video files using WebAssembly and/or WebGPU.

## Current State Analysis

The CLI version uses:
- **Whisper models** (tiny 40MB, base 140MB, small 460MB, medium 1.5GB, large 2.9GB)
- **Distil-Whisper** (distil-large-v3 ~750MB, distil-medium.en ~400MB)
- **Cohere Transcribe** (2-4GB)
- **NeMo ASR** (GPU only, not web-viable)

For web, we're limited to models that can:
1. Be converted to ONNX format
2. Run in browser memory constraints
3. Perform reasonably on CPU/WASM or WebGPU

## Technology Landscape

### Transformers.js (@xenova/transformers)

**Status:** Mature, actively maintained, proven in production

- ONNX Runtime-based execution in browser
- Supports CPU (WASM) and WebGPU backends
- Pipeline API similar to Python transformers
- **Whisper is fully supported**
- Quantization options: q8 (WASM default), q4, fp16, fp32 (WebGPU default)

**Key capabilities:**
- Automatic Speech Recognition pipeline
- Multilingual support
- Can use quantized models to reduce size
- Models loaded from Hugging Face Hub or local files

**Existing implementation:** xenova/whisper-web
- Demo site with full Whisper implementation
- Supports file upload, microphone recording
- Has experimental WebGPU support
- ~3.3k stars, active development

### WebGPU

**Status:** Available in Chrome 113+, Edge 113+, Safari 18.2+, Firefox (behind flag)

- Direct GPU access for compute
- Significant speedup over WASM
- Still experimental in some browsers
- Requires https:// or localhost

### WebNN API

**Status:** Emerging, limited browser support

- Chrome 123+ has backend support (behind flags)
- Hardware acceleration for neural network operations
- Not yet widely available enough to rely on

### ONNX Runtime Web

**Status:** Mature, production-ready

- Backend for Transformers.js
- Supports WebAssembly and WebGPU
- Good performance on both CPU and GPU

## Design Options

### Option A: Transformers.js + ONNX (Recommended)

**Approach:** Use Transformers.js as the core engine

**Pros:**
- Battle-tested library with active maintenance
- API similar to Python version (easy port)
- Supports both WASM and WebGPU backends
- Multilingual support built-in
- Model quantization reduces bandwidth/memory

**Cons:**
- Dependent on external library
- Initial model download required

**Model Options (with quantization):**
| Model | Size (q8) | Size (q4) | Best for |
|-------|-----------|-----------|----------|
| Xenova/whisper-tiny | ~40MB | ~20MB | Fastest, lower accuracy |
| Xenova/whisper-base | ~140MB | ~70MB | Balance of speed/accuracy |
| Xenova/whisper-small | ~460MB | ~230MB | Better accuracy |

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                     Browser UI                          │
│  - File upload (drag & drop)                            │
│  - URL input (for direct download)                      │
│  - Progress indicator                                   │
│  - Model selection                                      │
│  - Language selection                                   │
│  - Transcript output (copy, download)                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Audio Processing Layer                     │
│  - Web Audio API for decoding                           │
│  - AudioContext for normalization (16kHz mono)          │
│  - Chunking for long files                              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Transformers.js Engine                     │
│  - Pipeline: automatic-speech-recognition              │
│  - Backend: WebGPU (if available) or WASM              │
│  - Model: Quantized Whisper variants                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Model Storage (IndexedDB)                  │
│  - Cache models locally after first download            │
│  - Offline capability for repeated use                 │
└─────────────────────────────────────────────────────────┘
```

### Option B: Pure WebGPU + Custom ONNX

**Approach:** Use ONNX Runtime Web directly with WebGPU

**Pros:**
- More control over the execution
- Potentially better performance optimization
- Smaller bundle (no Transformers.js overhead)

**Cons:**
- More development effort
- Need to handle preprocessing/postprocessing manually
- Tokenization, feature extraction all custom

### Option C: Web Workers + WASM Only

**Approach:** Multi-threaded WASM without GPU

**Pros:**
- Maximum browser compatibility
- Predictable performance across devices

**Cons:**
- Slower than GPU options
- Still needs ONNX Runtime

## Implementation Plan (Option A - Recommended)

### Phase 1: MVP (Single File Transcription)

**Tech Stack:**
- Vanilla JS + HTML (no build step for simplicity)
- OR: Vite + TypeScript for better developer experience
- Transformers.js from CDN (`@xenova/transformers`)

**Features:**
1. File upload (audio/video)
2. Model selection (tiny, base - default: tiny)
3. Progress bar during model loading and transcription
4. Transcript display with copy/download buttons
5. IndexedDB caching for models

**Key Code Structure:**
```javascript
// Core transcription function
import { pipeline } from '@xenova/transformers';

async function transcribe(audioFile, modelName, language) {
  // 1. Load model (cached after first load)
  const transcriber = await pipeline('automatic-speech-recognition',
    `Xenova/whisper-${modelName}`, {
      quantized: true,
      progress_callback: updateProgress
    });

  // 2. Process audio
  const audioContext = new AudioContext();
  const audioBuffer = await audioContext.decodeAudioData(audioFile);
  // Resample to 16kHz mono if needed

  // 3. Transcribe
  const result = await transcriber(audioBuffer, {
    language: language,
    chunk_length_s: 30,
    stride_length_s: 5
  });

  return result;
}
```

### Phase 2: Enhanced Features

1. **Real-time transcription** (microphone input)
   - Web Speech API as fallback for streaming
   - Or chunked processing with MediaRecorder

2. **YouTube/URL support**
   - CORS proxy for audio extraction
   - Or use yt-dlp as external preprocessor (user-side)

3. **Multi-language UI**
   - i18n for interface
   - Language detection option

4. **Timestamp output**
   - Word-level timestamps
   - Export as SRT/VTT

### Phase 3: Performance & UX

1. **WebGPU acceleration** (when available)
   - Auto-detect and switch
   - Fallback to WASM

2. **Model management**
   - Download multiple models
   - Clear cache option
   - Size indicators

3. **Advanced audio processing**
   - Noise reduction (Web Audio API filters)
   - Volume normalization

## Deployment Options

### Static Hosting (Simplest)

- GitHub Pages
- Netlify
- Cloudflare Pages
- Any static file host

**Why:** No backend needed, models fetched from Hugging Face CDN

### Self-Contained Version

For true "single file" experience like the CLI:

1. **Bundled HTML** with embedded scripts
2. **Local model files** served alongside
3. **PWA** for installability

Limitation: Models must still be downloaded (can't embed 40MB+ in HTML)

## Browser Compatibility

| Feature | Chrome | Edge | Firefox | Safari |
|---------|--------|------|---------|--------|
| WASM (CPU) | ✅ | ✅ | ✅ | ✅ |
| WebGPU | ✅ 113+ | ✅ 113+ | ⚠️ flag | ✅ 18.2+ |
| Web Audio | ✅ | ✅ | ✅ | ✅ |
| IndexedDB | ✅ | ✅ | ✅ | ✅ |

**Recommendation:** Build for WASM first, add WebGPU as enhancement

## Performance Expectations

Based on xenova/whisper-web benchmarks:

| Model | Hardware | Speed (real-time factor) |
|-------|----------|--------------------------|
| tiny (q8) | CPU (M1) | ~0.3x (3x faster) |
| tiny (q8) | CPU (x86) | ~0.5x (2x faster) |
| base (q8) | CPU (M1) | ~0.5x (2x faster) |
| base (q8) | WebGPU | ~0.1x (10x faster) |

WebGPU can approach real-time transcription for smaller models.

## Alternatives Considered

### MediaPipe Speech

- Google's solution for on-device speech
- More focused on voice commands
- Less flexible for general transcription

### Web Speech API

- Built into browsers
- Requires internet connection (usually)
- Limited language support
- No control over model

### Sherpa-ONNX

- Another ONNX-based solution
- Good for streaming ASR
- Less mature than Transformers.js for this use case

## Key Challenges

1. **YouTube/URL support in browser**
   - CORS restrictions prevent direct download
   - Solution: Use a CORS proxy or require users to download first
   - Alternative: yt-dlp wasm build (large, complex)

2. **Video file handling**
   - Browsers can't extract audio from all video formats
   - Solution: Use HTMLMediaElement + Web Audio API
   - Fallback: User extracts audio first

3. **Memory constraints**
   - Large files can crash browser tabs
   - Solution: Chunked processing, clear intermediate buffers

4. **Model distribution**
   - Hugging Face Hub has rate limits
   - Solution: Mirror models on own CDN, use IndexedDB caching

## File Size Comparison

| Component | Size |
|-----------|------|
| Transformers.js (minified) | ~500KB |
| ONNX Runtime WASM | ~2MB |
| Whisper-tiny (q8) | ~40MB |
| Whisper-base (q8) | ~140MB |
| Whisper-small (q8) | ~460MB |

Initial download: ~2.5MB (JS runtime) + model size

## Next Steps

1. **Create a proof-of-concept**
   - Basic HTML page with Transformers.js
   - Single file upload
   - Whisper-tiny model
   - Verify it works

2. **Build the UI**
   - Match typeout CLI aesthetics
   - Progress indicators
   - Model/language selection

3. **Package for distribution**
   - Single HTML file option
   - Or minimal npm package

4. **Test across browsers**
   - Chrome, Firefox, Safari
   - Mobile browsers

## References

- Transformers.js: https://huggingface.co/docs/transformers.js
- xenova/whisper-web: https://github.com/xenova/whisper-web
- ONNX Runtime Web: https://onnxruntime.ai/docs/js/
- WebGPU: https://developer.chrome.com/docs/web-platform/webgpu/
