import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../../context/AppContext';
import { Send, Mic, MicOff, Paperclip, X } from 'lucide-react';

export const ChatInput = ({ onSend, isLoading }) => {
  const { t } = useLanguage();
  const [text, setText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-grow textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!text.trim() && !attachedFile) return;
    if (isLoading) return;

    // Call send handler
    onSend(text, attachedFile);
    
    // Reset state
    setText("");
    setAttachedFile(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    // If Enter (without Shift) is pressed, submit the form
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleMicrophoneClick = () => {
    if (isRecording) {
      setIsRecording(false);
      // Mock typing speech result
      setText((prev) => prev + (prev ? " " : "") + "register a agricultural cooperative");
    } else {
      setIsRecording(true);
      // Mock voice listening state
      setTimeout(() => {
        setIsRecording(false);
        setText((prev) => prev + (prev ? " " : "") + "How do I register a cooperative?");
      }, 3000);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAttachedFile(file);
    }
  };

  const removeAttachedFile = () => {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 p-4 transition-colors">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-3">
        
        {/* Attachment Pill Preview */}
        {attachedFile && (
          <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-3 py-1.5 rounded-lg w-max max-w-full animate-message-appear">
            <Paperclip className="h-4 w-4 text-slate-400 shrink-0" />
            <span className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate max-w-[200px]">
              {attachedFile.name}
            </span>
            <button
              type="button"
              onClick={removeAttachedFile}
              className="p-0.5 rounded-md hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        )}

        {/* Input Bar Wrapper */}
        <div className="flex items-end gap-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 focus-within:ring-2 focus-within:ring-primary-500/20 focus-within:border-primary-500 dark:focus-within:border-primary-400 transition-all">
          
          {/* File Attachment Button */}
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            className="hidden" 
            id="chat-file-input"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900 rounded-lg transition-colors shrink-0"
            title="Attach Document"
          >
            <Paperclip className="h-5 w-5" />
          </button>

          {/* Text Area or Audio Equalizer Listening Animation */}
          {isRecording ? (
            <div className="flex-1 flex items-center justify-between py-1.5 px-3 bg-red-50/50 dark:bg-red-950/10 rounded-lg border border-red-100/40 dark:border-red-900/20 select-none">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-red-500 animate-ping shrink-0"></span>
                <span className="text-xs font-bold text-red-650 dark:text-red-400">
                  Listening... Speak now
                </span>
              </div>
              
              {/* Dynamic equalizing sound wave bars */}
              <div className="flex items-end gap-1 h-6">
                <span className="w-1 bg-red-500 dark:bg-red-400 rounded-full animate-wave-bar animate-wave-bar-1" style={{ height: '100%' }}></span>
                <span className="w-1 bg-red-500 dark:bg-red-400 rounded-full animate-wave-bar animate-wave-bar-2" style={{ height: '100%' }}></span>
                <span className="w-1 bg-red-500 dark:bg-red-400 rounded-full animate-wave-bar animate-wave-bar-3" style={{ height: '100%' }}></span>
                <span className="w-1 bg-red-500 dark:bg-red-400 rounded-full animate-wave-bar animate-wave-bar-4" style={{ height: '100%' }}></span>
                <span className="w-1 bg-red-500 dark:bg-red-400 rounded-full animate-wave-bar animate-wave-bar-5" style={{ height: '100%' }}></span>
              </div>
            </div>
          ) : (
            <textarea
              ref={textareaRef}
              rows={1}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t('chatPlaceholder')}
              disabled={isLoading}
              className="flex-1 resize-none bg-transparent py-1.5 px-1 border-0 focus:ring-0 text-slate-850 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-sm focus:outline-none min-h-[36px] max-h-[120px]"
            />
          )}

          {/* Voice Input Button */}
          <button
            type="button"
            onClick={handleMicrophoneClick}
            className={`p-2 rounded-lg transition-colors shrink-0 ${
              isRecording 
                ? 'bg-red-50 text-red-500 dark:bg-red-950/20 animate-pulse' 
                : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900'
            }`}
            title={isRecording ? "Recording... Click to stop" : "Voice Input"}
          >
            {isRecording ? <Mic className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </button>

          {/* Send Button */}
          <button
            type="submit"
            disabled={(!text.trim() && !attachedFile) || isLoading}
            className={`p-2.5 rounded-xl text-white shadow-sm transition-all shrink-0 ${
              (text.trim() || attachedFile) && !isLoading
                ? 'bg-primary-600 hover:bg-primary-700 dark:bg-primary-600 dark:hover:bg-primary-700 hover:scale-105 active:scale-100'
                : 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed'
            }`}
            title="Send Message"
          >
            <Send className="h-4.5 w-4.5" />
          </button>

        </div>

        {/* Dynamic Disclaimer / Typing Indicator */}
        <div className="text-center px-4">
          <p className="text-[10px] sm:text-[11px] text-slate-400 dark:text-slate-500 leading-normal">
            {t('chatDisclaimer')}
          </p>
        </div>

      </form>
    </div>
  );
};
export default ChatInput;
