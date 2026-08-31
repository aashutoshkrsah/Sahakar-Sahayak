import React, { useState } from 'react';
import { useLanguage, useAppData } from '../context/AppContext';
import { LayoutWrapper } from '../components/layout/LayoutWrapper';
import { SearchBar } from '../components/common/SearchBar';
import { EmptyState } from '../components/common/EmptyState';
import { History, MessageSquare, Trash2, Edit2, Check, X, ArrowRight, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const ChatHistory = () => {
  const { t } = useLanguage();
  const { chatHistory, deleteChat, renameChat } = useAppData();
  const navigate = useNavigate();

  const [searchQuery, setSearchQuery] = useState("");
  const [editingChatId, setEditingChatId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");

  const handleOpenChat = (id) => {
    navigate('/chat', { state: { resumeChatId: id } });
  };

  const handleStartRename = (e, id, currentTitle) => {
    e.stopPropagation();
    setEditingChatId(id);
    setEditingTitle(currentTitle);
  };

  const handleSaveRename = (e, id) => {
    e.stopPropagation();
    if (editingTitle.trim()) {
      renameChat(id, editingTitle.trim());
    }
    setEditingChatId(null);
  };

  const handleCancelRename = (e) => {
    e.stopPropagation();
    setEditingChatId(null);
  };

  const handleDelete = (e, id) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this chat conversation?")) {
      deleteChat(id);
    }
  };

  // Filter history
  const filteredHistory = chatHistory.filter(chat => {
    if (!searchQuery) return true;
    const lowerQuery = searchQuery.toLowerCase();
    return (
      chat.title.toLowerCase().includes(lowerQuery) ||
      chat.lastMessage.toLowerCase().includes(lowerQuery) ||
      chat.category.toLowerCase().includes(lowerQuery)
    );
  });

  // Group history chronologically
  const getGroup = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays <= 1) {
      return "Today";
    } else if (diffDays <= 7) {
      return "Previous 7 Days";
    } else {
      return "Older";
    }
  };

  const groupedChats = {
    "Today": [],
    "Previous 7 Days": [],
    "Older": []
  };

  filteredHistory.forEach(chat => {
    const group = getGroup(chat.date);
    groupedChats[group].push(chat);
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <LayoutWrapper title={t('chatHistory')}>
      <div className="space-y-6 text-left animate-message-appear">
        
        {/* Title */}
        <div>
          <h2 className="text-xl font-bold font-display text-slate-800 dark:text-white">
            {t('chatHistory')}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Access, continue, or manage past chat sessions with Sahayak.
          </p>
        </div>

        {chatHistory.length === 0 ? (
          /* Empty State */
          <EmptyState
            title="No Conversations Yet"
            description="You haven't initiated any legal guidance chats with Sahayak. Ask your first question now!"
            actionText={t('askFirstQuestion')}
            onActionClick={() => navigate('/chat')}
            icon={History}
          />
        ) : (
          <>
            {/* Search Input */}
            <SearchBar
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onClear={() => setSearchQuery("")}
              placeholder="Search in chat history..."
            />

            {/* Render chronological sections */}
            <div className="space-y-6">
              {Object.keys(groupedChats).map((groupName) => {
                const groupItems = groupedChats[groupName];
                if (groupItems.length === 0) return null;

                return (
                  <div key={groupName} className="space-y-3">
                    <h3 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider pl-1.5 flex items-center gap-1.5">
                      <Calendar className="h-4 w-4" />
                      {groupName}
                    </h3>
                    
                    <div className="space-y-3">
                      {groupItems.map((chat) => (
                        <div
                          key={chat.id}
                          onClick={() => handleOpenChat(chat.id)}
                          className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-4 sm:p-5 flex justify-between items-center gap-4 hover:shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-all cursor-pointer group"
                        >
                          <div className="flex gap-3.5 items-center min-w-0 flex-1">
                            <div className="h-10 w-10 bg-slate-50 dark:bg-slate-950 text-slate-450 dark:text-slate-500 rounded-xl flex items-center justify-center shrink-0 group-hover:text-primary-655 transition-colors">
                              <MessageSquare className="h-5 w-5" />
                            </div>
                            
                            <div className="min-w-0 flex-1 space-y-1">
                              {/* Edit Title Check */}
                              {editingChatId === chat.id ? (
                                <div className="flex items-center gap-1.5 max-w-lg" onClick={(e) => e.stopPropagation()}>
                                  <input
                                    type="text"
                                    value={editingTitle}
                                    onChange={(e) => setEditingTitle(e.target.value)}
                                    className="bg-slate-50 dark:bg-slate-950 border border-slate-250 dark:border-slate-800 rounded px-2.5 py-1 text-xs font-semibold text-slate-800 dark:text-slate-100 focus:outline-none focus:border-primary-500 flex-1 min-w-[120px]"
                                  />
                                  <button
                                    onClick={(e) => handleSaveRename(e, chat.id)}
                                    className="p-1 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 rounded"
                                  >
                                    <Check className="h-4.5 w-4.5" />
                                  </button>
                                  <button
                                    onClick={handleCancelRename}
                                    className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 rounded"
                                  >
                                    <X className="h-4.5 w-4.5" />
                                  </button>
                                </div>
                              ) : (
                                <h4 className="text-xs sm:text-sm font-bold text-slate-850 dark:text-white truncate">
                                  {chat.title}
                                </h4>
                              )}

                              <p className="text-xs text-slate-400 dark:text-slate-500 truncate max-w-xl">
                                {chat.lastMessage}
                              </p>
                              
                              <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-400">
                                <span className="bg-slate-100 dark:bg-slate-850 text-slate-500 dark:text-slate-400 px-2 py-0.2 rounded-full font-bold">
                                  {chat.category}
                                </span>
                                <span className="bg-slate-100 dark:bg-slate-850 text-slate-500 dark:text-slate-400 px-2 py-0.2 rounded-full font-bold uppercase">
                                  {chat.language}
                                </span>
                                <span className="font-semibold">{formatDate(chat.date)}</span>
                              </div>
                            </div>
                          </div>

                          {/* Row Actions */}
                          <div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
                            <button
                              onClick={(e) => handleStartRename(e, chat.id, chat.title)}
                              className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-400 hover:text-slate-655 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                              title="Rename Conversation"
                              aria-label="Rename Conversation"
                            >
                              <Edit2 className="h-4 w-4" />
                            </button>
                            
                            <button
                              onClick={(e) => handleDelete(e, chat.id)}
                              className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/10 transition-colors"
                              title="Delete Conversation"
                              aria-label="Delete Conversation"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>

                            <button
                              onClick={() => handleOpenChat(chat.id)}
                              className="p-2 rounded-lg text-slate-400 group-hover:text-primary-600 dark:group-hover:text-primary-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors shrink-0"
                              title="Open Chat"
                            >
                              <ArrowRight className="h-4.5 w-4.5" />
                            </button>
                          </div>

                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}

      </div>
    </LayoutWrapper>
  );
};
export default ChatHistory;
