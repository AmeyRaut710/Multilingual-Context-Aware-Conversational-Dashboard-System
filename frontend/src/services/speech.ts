export interface SpeechRecognitionResultHandler {
  onResult: (transcript: string, isFinal: boolean) => void;
  onError: (error: string) => void;
  onEnd: () => void;
}

export class SpeechService {
  private recognition: any = null;
  private isListening: boolean = false;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor() {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US'; // default, dynamically switchable to hi-IN, mr-IN
    }
  }

  public isSupported(): boolean {
    return !!this.recognition || !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  public setLanguage(langCode: 'en-US' | 'hi-IN' | 'mr-IN') {
    if (this.recognition) {
      this.recognition.lang = langCode;
    }
  }

  public startListening(
    lang: 'en-US' | 'hi-IN' | 'mr-IN',
    handlers: SpeechRecognitionResultHandler
  ): boolean {
    if (this.recognition) {
      try {
        this.recognition.lang = lang;
        this.recognition.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }

          if (finalTranscript) {
            handlers.onResult(finalTranscript, true);
          } else if (interimTranscript) {
            handlers.onResult(interimTranscript, false);
          }
        };

        this.recognition.onerror = (event: any) => {
          handlers.onError(event.error || 'Speech recognition error');
        };

        this.recognition.onend = () => {
          this.isListening = false;
          handlers.onEnd();
        };

        this.recognition.start();
        this.isListening = true;
        return true;
      } catch (err: any) {
        handlers.onError(err.message || 'Failed to start speech recognition');
        return false;
      }
    }
    return false;
  }

  public stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }
}

export const speechService = new SpeechService();
