import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, MicOff, Send, Sparkles, AlertCircle, Bot, User, 
  ChevronDown, ChevronUp, Globe2, HelpCircle, CornerDownLeft 
} from 'lucide-react';
import { speechService } from '../services/speech';
import { ClarificationQuestion } from '../types/dashboard';

interface Message {
  sender: 'user' | 'system';
  text: string;
  language?: string;
  clarification?: ClarificationQuestion;
  timestamp: string;
}

interface ChatAssistantProps {
  onSendCommand: (command: string) => Promise<any>;
  isLoading: boolean;
  history: { user_command: string; system_response: string; intent: string }[];
  pendingClarification?: ClarificationQuestion;
  onResolveClarification: (answer: string) => void;
}

export const ChatAssistant: React.FC<ChatAssistantProps> = ({
  onSendCommand,
  isLoading,
  history,
  pendingClarification,
  onResolveClarification,
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceLang, setVoiceLang] = useState<'en-US' | 'hi-IN' | 'mr-IN'>('en-US');
  const [speechError, setSpeechError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history, pendingClarification, isLoading]);

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;
    const cmd = inputText.trim();
    setInputText('');
    await onSendCommand(cmd);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const toggleMic = () => {
    if (isListening) {
      speechService.stopListening();
      setIsListening(false);
    } else {
      setSpeechError(null);
      const started = speechService.startListening(voiceLang, {
        onResult: (transcript, isFinal) => {
          setInputText(transcript);
          if (isFinal) {
            setIsListening(false);
            // Optionally auto-send on final speech
          }
        },
        onError: (err) => {
          setSpeechError(err);
          setIsListening(false);
        },
        onEnd: () => {
          setIsListening(false);
        },
      });

      if (started) {
        setIsListening(true);
      } else {
        setSpeechError('Speech recognition is not supported in this browser or permission denied.');
      }
    }
  };

  const samplePrompts = [
    { label: 'Monthly sales bar chart', cmd: 'Create a bar chart of monthly sales', lang: 'EN' },
    { label: 'Ekun revenue dakhva', cmd: 'Ekun revenue dakhva', lang: 'MR' },
    { label: 'Sales ka bar chart banao', cmd: 'Monthly sales ka bar chart banao', lang: 'HI' },
    { label: 'Top 5 products by profit', cmd: 'Top 5 products by profit dikhao', lang: 'Mix' },
    { label: 'Change it to pie chart', cmd: 'Change it to a pie chart', lang: 'Context' },
  ];

  return (
    <div
      className={`fixed bottom-4 right-4 z-40 w-full sm:w-[420px] transition-all duration-300 ${
        isOpen ? 'h-[520px]' : 'h-14'
      } flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden`}
    >
      {/* Header */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="h-14 px-4 bg-gradient-to-r from-brand-600 to-indigo-600 text-white flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold flex items-center">
              AI Dashboard Assistant
            </h3>
            <p className="text-[10px] text-white/80">
              English • Hindi • Marathi • Code-mixed
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </div>
      </div>

      {isOpen && (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-50/60 dark:bg-slate-950/40 text-xs">
            {/* Intro Welcome */}
            <div className="flex items-start space-x-2.5">
              <div className="w-6 h-6 rounded-full bg-brand-100 dark:bg-brand-900 flex items-center justify-center text-brand-600 dark:text-brand-300 shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5" />
              </div>
              <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl rounded-tl-sm p-3 shadow-sm max-w-[85%] text-slate-800 dark:text-slate-200">
                <p className="font-semibold text-brand-600 dark:text-brand-400 mb-1">
                  Namaste & Welcome! 🙏
                </p>
                <p>
                  You can tell me to generate charts, calculate KPIs, or apply filters in English, Hindi, or Marathi.
                </p>
              </div>
            </div>

            {/* Conversation History */}
            {history.map((turn, idx) => (
              <React.Fragment key={idx}>
                {/* User Message */}
                <div className="flex items-start justify-end space-x-2">
                  <div className="bg-brand-600 text-white rounded-2xl rounded-tr-sm p-3 shadow-sm max-w-[85%]">
                    <p>{turn.user_command}</p>
                  </div>
                  <div className="w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300 shrink-0 mt-0.5">
                    <User className="w-3.5 h-3.5" />
                  </div>
                </div>

                {/* System Response */}
                <div className="flex items-start space-x-2">
                  <div className="w-6 h-6 rounded-full bg-brand-100 dark:bg-brand-900 flex items-center justify-center text-brand-600 dark:text-brand-300 shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                  <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl rounded-tl-sm p-3 shadow-sm max-w-[85%] text-slate-800 dark:text-slate-200">
                    <p>{turn.system_response}</p>
                  </div>
                </div>
              </React.Fragment>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex items-center space-x-2 text-slate-400 dark:text-slate-500 italic">
                <div className="w-2 h-2 rounded-full bg-brand-500 animate-pulse" />
                <span>Processing multilingual command...</span>
              </div>
            )}

            {/* Pending Clarification Prompt */}
            {pendingClarification && (
              <div className="bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800 rounded-xl p-3.5 shadow-sm">
                <div className="flex items-center space-x-1.5 text-amber-700 dark:text-amber-400 font-bold mb-1.5">
                  <HelpCircle className="w-4 h-4 shrink-0" />
                  <span>Clarification Required</span>
                </div>
                <p className="text-amber-900 dark:text-amber-200 mb-2.5">
                  {pendingClarification.question}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {pendingClarification.options.map((opt) => (
                    <button
                      key={opt}
                      onClick={() => onResolveClarification(opt)}
                      className="px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-semibold transition-colors shadow-sm"
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Speech Error Banner */}
            {speechError && (
              <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 text-[11px] flex items-center space-x-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>{speechError}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts Carousel */}
          <div className="px-3 py-1.5 bg-slate-100/70 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 flex items-center gap-1.5 overflow-x-auto no-scrollbar text-[11px]">
            <span className="text-slate-400 font-semibold shrink-0">Try:</span>
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => setInputText(p.cmd)}
                className="shrink-0 px-2 py-0.5 rounded-full bg-white dark:bg-slate-700 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 border border-slate-200 dark:border-slate-600 transition-colors"
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Input & Voice Controls */}
          <div className="p-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
            {/* Language Dialect Selector */}
            <div className="flex items-center justify-between mb-2 text-[11px] text-slate-500">
              <div className="flex items-center space-x-1">
                <Globe2 className="w-3 h-3 text-brand-600" />
                <span>Speech Language:</span>
                <select
                  value={voiceLang}
                  onChange={(e) => setVoiceLang(e.target.value as any)}
                  className="bg-transparent font-medium text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer"
                >
                  <option value="en-US" className="dark:bg-slate-900">English (US/India)</option>
                  <option value="hi-IN" className="dark:bg-slate-900">Hindi (हिन्दी)</option>
                  <option value="mr-IN" className="dark:bg-slate-900">Marathi (मराठी)</option>
                </select>
              </div>
              {isListening && (
                <span className="flex items-center text-rose-500 font-semibold animate-pulse">
                  <span className="w-2 h-2 rounded-full bg-rose-500 mr-1" /> Listening...
                </span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {/* Mic Button */}
              <button
                type="button"
                onClick={toggleMic}
                className={`p-2.5 rounded-xl transition-all ${
                  isListening
                    ? 'bg-rose-500 text-white animate-pulse ring-4 ring-rose-500/20 shadow-md'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-brand-50 hover:text-brand-600 dark:hover:bg-slate-700'
                }`}
                title={isListening ? 'Stop listening' : 'Start voice command'}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>

              {/* Text Input */}
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  isListening
                    ? 'Listening... speak now'
                    : 'Type instruction in English, Hindi, or Marathi...'
                }
                disabled={isLoading}
                className="flex-1 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
              />

              {/* Send Button */}
              <button
                type="button"
                onClick={handleSend}
                disabled={!inputText.trim() || isLoading}
                className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors shadow-sm"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

