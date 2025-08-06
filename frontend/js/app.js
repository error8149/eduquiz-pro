// app.js

// Configuration loading
const getConfig = async () => {
    try {
        const response = await fetch('/config');
        if (response.ok) {
            const config = await response.json();
            console.log('📡 Loaded config:', config);
            return config;
        }
    } catch (error) {
        console.warn('⚠️  Could not fetch config, using defaults:', error);
    }
    
    // Fallback configuration
    const fallbackConfig = {
        api_base_url: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://127.0.0.1:8000/api/v1'
            : '/api/v1',
        app_name: 'EduQuiz Pro',
        version: '1.0.0',
        environment: 'development',
        base_url: window.location.origin,
        defaults: {
            ai_provider: 'gemini',
            grade_level: 'high school',
            difficulty: 'medium',
            num_questions: 10,
            time_limit: 15
        }
    };
    
    console.log('🔧 Using fallback config:', fallbackConfig);
    return fallbackConfig;
};

// Initialize app with dynamic configuration
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initializing EduQuiz Pro...');
    
    // Load configuration
    const config = await getConfig();
    const API_BASE_URL = config.api_base_url; // ✅ FIXED: Use config-based URL
    
    console.log(`🌐 API Base URL: ${API_BASE_URL}`);
    console.log(`🏠 Environment: ${config.environment}`);
    
    const state = {
        config,
        currentView: 'setup',
        settings: { 
            totalQuestions: config.defaults.num_questions,
            totalTime: config.defaults.time_limit,
            gradeLevel: config.defaults.grade_level,
            difficulty: config.defaults.difficulty,
            apiKeys: { gemini: '', openai: '', groq: '' },
            topics: { 
                "Computer Science": ["Algorithms", "Data Structures", "Programming"], 
                "General Knowledge": ["History", "Geography", "Science"],
                "Mathematics": ["Algebra", "Geometry", "Calculus"],
                "Science": ["Physics", "Chemistry", "Biology"]
            }
        },
        quiz: { questions: [], currentQuestionIndex: 0, score: 0, timerId: null, timeRemaining: 0, startTime: null, userAnswers: [] },
        historyFilter: { mode: '', date: '' }
    };

    const dom = {
        views: {
            setup: document.getElementById('setup-view'),
            quiz: document.getElementById('quiz-view'),
            results: document.getElementById('results-view'),
            history: document.getElementById('history-view'),
            settings: document.getElementById('settings-view')
        },
        navLinks: document.querySelectorAll('.nav-btn'),
        toast: {
            el: document.getElementById('toast'),
            message: document.getElementById('toast-message'),
            icon: document.getElementById('toast-icon'),
            progress: document.getElementById('toast-progress')
        },
        loadingModal: {
            el: document.getElementById('loading-modal'),
            message: document.getElementById('loading-message')
        },
    };

    // ✅ REMOVED: Duplicate API_BASE_URL declaration that was overriding the config

    const showToast = (message, isError = false) => {
        dom.toast.message.textContent = message;
        dom.toast.icon.className = `fas ${isError ? 'fa-exclamation-circle text-red-500' : 'fa-check-circle text-green-500'} mr-3 text-xl`;
        dom.toast.progress.className = `absolute bottom-0 left-0 h-1 ${isError ? 'bg-red-500' : 'bg-green-500'} rounded-b-xl toast-progress-bar`;
        dom.toast.el.classList.remove('hidden');
        setTimeout(() => dom.toast.el.classList.add('hidden'), 4000);
    };

    const logErrorToBackend = async (error, context, responseText = '') => {
        try {
            const response = await fetch(`${API_BASE_URL}/log-error`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    error: error.message, 
                    stack: error.stack, 
                    context, 
                    responseText,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });
            if (!response.ok) {
                console.error('Failed to log error to backend:', await response.text());
            }
        } catch (e) {
            console.error('Failed to log error to backend:', e);
        }
    };

    const showLoadingModal = (message) => {
        dom.loadingModal.message.textContent = message;
        dom.loadingModal.el.classList.remove('hidden');
    };

    const hideLoadingModal = () => {
        dom.loadingModal.el.classList.add('hidden');
    };

    const switchView = (viewName) => {
        console.log(`Switching to view: ${viewName}`);
        state.currentView = viewName;

        Object.entries(dom.views).forEach(([key, view]) => {
            if (!view) {
                console.error(`View container for ${key} not found in DOM`);
                return;
            }
            view.classList.add('hidden');
            view.classList.remove('active');
            view.innerHTML = '';
        });

        if (!dom.views[viewName]) {
            console.error(`View container for ${viewName} not found`);
            showToast(`View ${viewName} not found`, true);
            state.currentView = 'setup';
            renderSetupView();
            dom.views.setup.classList.remove('hidden');
            return;
        }

        const renderers = {
            setup: renderSetupView,
            quiz: renderQuizView,
            results: renderResultsView,
            history: renderHistoryView,
            settings: renderSettingsView
        };

        if (renderers[viewName]) {
            try {
                renderers[viewName]();
                dom.views[viewName].classList.remove('hidden');
                dom.views[viewName].classList.add('active');
            } catch (error) {
                console.error(`Error rendering ${viewName} view:`, error);
                showToast(`Failed to render ${viewName} view`, true);
                logErrorToBackend(error, `render${viewName.charAt(0).toUpperCase() + viewName.slice(1)}View`);
                state.currentView = 'setup';
                renderSetupView();
                dom.views.setup.classList.remove('hidden');
            }
        }

        // Update active navigation link
        dom.navLinks.forEach(link => {
            if (link.dataset.view === viewName) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    };

    function renderSetupView() {
        dom.views.setup.innerHTML = `
            <div class="max-w-4xl mx-auto">
                <div class="glass-effect rounded-2xl shadow-2xl p-8 slide-in">
                    <div class="text-center mb-8">
                        <h2 class="text-4xl font-bold text-green-400 mb-3">Create Your Quiz</h2>
                        <p class="text-gray-400 text-lg">Configure your quiz and let AI generate personalized questions</p>
                    </div>
                    
                    <div class="grid md:grid-cols-2 gap-8 mb-8">
                        <div class="space-y-6">
                            <div>
                                <label for="grade-level" class="block mb-3 font-semibold text-lg text-green-400">
                                    <i class="fas fa-graduation-cap mr-2"></i>Grade Level
                                </label>
                                <select id="grade-level" class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none text-lg">
                                    <option value="elementary" ${state.settings.gradeLevel === 'elementary' ? 'selected' : ''}>Elementary School</option>
                                    <option value="middle school" ${state.settings.gradeLevel === 'middle school' ? 'selected' : ''}>Middle School</option>
                                    <option value="high school" ${state.settings.gradeLevel === 'high school' ? 'selected' : ''}>High School</option>
                                    <option value="college" ${state.settings.gradeLevel === 'college' ? 'selected' : ''}>College</option>
                                    <option value="graduate" ${state.settings.gradeLevel === 'graduate' ? 'selected' : ''}>Graduate</option>
                                </select>
                            </div>
                            
                            <div>
                                <label for="difficulty" class="block mb-3 font-semibold text-lg text-green-400">
                                    <i class="fas fa-chart-line mr-2"></i>Difficulty Level
                                </label>
                                <select id="difficulty" class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none text-lg">
                                    <option value="easy" ${state.settings.difficulty === 'easy' ? 'selected' : ''}>Easy - Basic concepts</option>
                                    <option value="medium" ${state.settings.difficulty === 'medium' ? 'selected' : ''}>Medium - Intermediate level</option>
                                    <option value="hard" ${state.settings.difficulty === 'hard' ? 'selected' : ''}>Hard - Advanced level</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="space-y-6">
                            <div>
                                <label for="ai-provider" class="block mb-3 font-semibold text-lg text-green-400">
                                    <i class="fas fa-robot mr-2"></i>AI Provider
                                </label>
                                <select id="ai-provider" class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none text-lg">
                                    <option value="gemini" ${config.defaults.ai_provider === 'gemini' ? 'selected' : ''}>Google Gemini</option>
                                    <option value="openai" ${config.defaults.ai_provider === 'openai' ? 'selected' : ''}>OpenAI GPT</option>
                                    <option value="groq" ${config.defaults.ai_provider === 'groq' ? 'selected' : ''}>Groq</option>
                                </select>
                            </div>
                            
                            <div>
                                <label for="num-questions" class="block mb-3 font-semibold text-lg text-green-400">
                                    <i class="fas fa-list-ol mr-2"></i>Number of Questions
                                </label>
                                <input type="number" id="num-questions" min="1" max="50" value="${state.settings.totalQuestions}" class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none text-lg">
                            </div>
                        </div>
                    </div>

                    <div class="flex justify-center mb-8 bg-gray-700 p-1 rounded-xl">
                        <button id="mode-toggle-ai" class="w-full py-3 rounded-xl bg-green-600 text-white font-semibold transition-all">
                            <i class="fas fa-magic mr-2"></i>AI Generation
                        </button>
                        <button id="mode-toggle-manual" class="w-full py-3 text-gray-300 font-semibold transition-all">
                            <i class="fas fa-edit mr-2"></i>Manual Input
                        </button>
                    </div>
                    
                    <div id="ai-mode-form" class="space-y-6">
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <h3 class="text-xl font-semibold mb-4 text-yellow-400">
                                <i class="fas fa-info-circle mr-2"></i>Selected Topics
                            </h3>
                            <div id="topics-display" class="space-y-3">
                                ${Object.entries(state.settings.topics).map(([section, topics]) => `
                                    <div class="bg-gray-600 p-4 rounded-lg">
                                        <h4 class="font-semibold text-green-400">${section}</h4>
                                        <p class="text-gray-300">${topics.join(', ')}</p>
                                    </div>
                                `).join('')}
                            </div>
                            <p class="text-sm text-gray-400 mt-4">
                                <i class="fas fa-cog mr-1"></i>
                                Manage topics in Settings
                            </p>
                        </div>
                    </div>
                    
                    <div id="manual-mode-form" class="hidden space-y-6">
                        <div class="flex justify-end mb-4">
                            <button id="generate-prompt-btn" type="button" class="bg-indigo-600 hover:bg-indigo-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                                <i class="fas fa-magic mr-2"></i>Generate AI Prompt
                            </button>
                        </div>
                        <div>
                            <label for="manual-questions-input" class="block mb-3 font-semibold text-lg text-green-400">
                                <i class="fas fa-code mr-2"></i>Paste Questions (JSON format)
                            </label>
                            <textarea id="manual-questions-input" rows="15" class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 font-mono text-sm focus:ring-2 focus:ring-green-500 focus:outline-none" placeholder='[{"question_text": "What is 2+2?", "options": ["3", "4", "5", "6"], "correct_answer": "4", "explanation": "2+2 equals 4.", "section": "Math", "topic": "Arithmetic"}]'></textarea>
                        </div>
                    </div>
                    
                    <div class="mt-10 text-center">
                        <button id="start-quiz-btn" class="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white py-4 px-12 rounded-xl text-xl font-bold transition-all transform hover:scale-105 shadow-xl">
                            <i class="fas fa-play mr-3"></i>Start Quiz
                        </button>
                    </div>
                </div>
            </div>`;
        addSetupEventListeners();
    }

    // ✅ UPDATE: Add dynamic app title and footer
    const updateAppInfo = () => {
        document.title = config.app_name;
        const footer = document.querySelector('footer p');
        if (footer) {
            footer.innerHTML = `&copy; 2025 ${config.app_name} v${config.version}. All rights reserved.`;
        }
    };

    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function renderQuizView() {
        if (!state.quiz.questions || state.quiz.questions.length === 0) {
            dom.views.quiz.innerHTML = `
                <div class="max-w-3xl mx-auto glass-effect rounded-2xl shadow-2xl p-8 text-center">
                    <h2 class="text-3xl font-bold text-red-400 mb-4">No Questions Available</h2>
                    <p class="text-gray-400 mb-6">Please configure and start a new quiz from the setup page.</p>
                    <button id="back-to-setup-btn" class="bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-xl font-semibold">Back to Setup</button>
                </div>`;
            document.getElementById('back-to-setup-btn').addEventListener('click', () => switchView('setup'));
            return;
        }
        
        const q = state.quiz.questions[state.quiz.currentQuestionIndex];
        const options = shuffleArray([...q.options]);
        const progress = ((state.quiz.currentQuestionIndex + 1) / state.quiz.questions.length) * 100;
        
        dom.views.quiz.innerHTML = `
            <div class="max-w-4xl mx-auto glass-effect rounded-2xl shadow-2xl p-8 fade-in">
                <div class="mb-6">
                    <div class="flex justify-between items-center mb-4">
                        <div>
                            <p class="font-bold text-2xl text-green-400">${q.section} - ${q.topic}</p>
                            <p class="text-gray-400 text-lg">Question ${state.quiz.currentQuestionIndex + 1} of ${state.quiz.questions.length}</p>
                        </div>
                        <div class="text-right">
                            <p class="text-xl">Score: <span class="font-bold text-green-500">${state.quiz.score}</span></p>
                            <p class="text-xl">Time: <span id="quiz-timer" class="font-bold text-yellow-400">--:--</span></p>
                        </div>
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-3 mb-6">
                        <div class="bg-gradient-to-r from-green-500 to-blue-500 h-3 rounded-full transition-all duration-300" style="width: ${progress}%"></div>
                    </div>
                </div>
                
                <div class="bg-gray-700 p-6 rounded-xl mb-8">
                    <p class="text-xl text-gray-100 leading-relaxed">${q.question_text}</p>
                </div>
                
                <div id="options-container" class="grid gap-4 mb-8">
                    ${options.map((opt, index) => `
                        <div class="option-card flex items-center p-5 bg-gray-700 hover:bg-gray-600 rounded-xl border-2 border-transparent cursor-pointer transition-all transform hover:scale-[1.02]" data-option="${escapeHTML(opt)}">
                            <div class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center mr-4 font-bold text-green-400">
                                ${String.fromCharCode(65 + index)}
                            </div>
                            <span class="text-lg">${escapeHTML(opt)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div id="explanation-container" class="hidden mb-8">
                    <div class="bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-xl">
                        <h4 class="font-bold text-xl text-white mb-3">
                            <i class="fas fa-lightbulb mr-2"></i>Explanation
                        </h4>
                        <p id="explanation-text" class="text-blue-100 leading-relaxed">${q.explanation || 'No explanation provided.'}</p>
                    </div>
                    <div class="mt-6 bg-gray-700 p-6 rounded-xl">
                        <h4 class="font-bold text-lg text-blue-400 mb-3">
                            <i class="fas fa-question-circle mr-2"></i>Ask AI for more details
                        </h4>
                        <div class="flex space-x-3">
                            <input id="ask-ai-input" type="text" class="flex-grow bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:outline-none" placeholder="e.g., Explain this concept further">
                            <button id="ask-ai-btn" class="bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                        <div id="ai-response-box" class="mt-4 p-4 bg-gray-600 rounded-xl text-sm hidden"></div>
                    </div>
                </div>
                
                <div class="flex justify-between items-center">
                    <button id="end-quiz-btn" class="bg-red-600 hover:bg-red-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                        <i class="fas fa-stop mr-2"></i>End Quiz
                    </button>
                    <button id="next-question-btn" class="bg-green-600 hover:bg-green-700 text-white py-3 px-8 rounded-xl font-semibold hidden transition-all">
                        <i class="fas fa-arrow-right mr-2"></i>Next Question
                    </button>
                </div>
            </div>`;
        addQuizEventListeners();
        startTimer();
    }

    function renderResultsView() {
        const { score, questions, userAnswers, startTime } = state.quiz;
        const timeTaken = Math.round((new Date() - startTime) / 1000);
        const percentage = questions.length > 0 ? Math.round((score / questions.length) * 100) : 0;
        const incorrectQuestions = userAnswers.filter(ans => ans.userAnswer !== ans.correct_answer);
        
        let performanceColor = 'text-red-400';
        let performanceIcon = 'fa-frown';
        if (percentage >= 80) {
            performanceColor = 'text-green-400';
            performanceIcon = 'fa-smile';
        } else if (percentage >= 60) {
            performanceColor = 'text-yellow-400';
            performanceIcon = 'fa-meh';
        }
        
        dom.views.results.innerHTML = `
            <div class="max-w-5xl mx-auto">
                <div class="glass-effect rounded-2xl p-8 text-center fade-in mb-8">
                    <h2 class="text-5xl font-bold mb-4">Quiz Completed!</h2>
                    <div class="${performanceColor} text-8xl font-bold mb-8 flex items-center justify-center">
                        <i class="fas ${performanceIcon} mr-4"></i>
                        ${percentage}%
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <i class="fas fa-trophy text-yellow-400 text-3xl mb-2"></i>
                            <p class="text-gray-400">Final Score</p>
                            <p class="text-3xl font-bold">${score}/${questions.length}</p>
                        </div>
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <i class="fas fa-clock text-blue-400 text-3xl mb-2"></i>
                            <p class="text-gray-400">Time Taken</p>
                            <p class="text-3xl font-bold">${Math.floor(timeTaken / 60).toString().padStart(2, '0')}:${(timeTaken % 60).toString().padStart(2, '0')}</p>
                        </div>
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <i class="fas fa-check text-green-400 text-3xl mb-2"></i>
                            <p class="text-gray-400">Correct</p>
                            <p class="text-3xl font-bold">${score}</p>
                        </div>
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <i class="fas fa-times text-red-400 text-3xl mb-2"></i>
                            <p class="text-gray-400">Incorrect</p>
                            <p class="text-3xl font-bold">${questions.length - score}</p>
                        </div>
                    </div>
                </div>
                
                ${incorrectQuestions.length > 0 ? `
                    <div class="glass-effect rounded-2xl p-8 mb-8">
                        <h3 class="text-2xl font-bold mb-6 text-red-400">
                            <i class="fas fa-exclamation-triangle mr-2"></i>
                            Review Incorrect Answers (${incorrectQuestions.length})
                        </h3>
                        <div class="space-y-4 max-h-96 overflow-y-auto">
                            ${incorrectQuestions.map((ans, i) => `
                                <div class="bg-gray-700 p-4 rounded-xl border-l-4 border-red-400">
                                    <p class="font-semibold mb-2">${ans.question_text}</p>
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                        <p class="text-red-300">Your Answer: ${ans.userAnswer || 'None'}</p>
                                        <p class="text-green-300">Correct Answer: ${ans.correct_answer}</p>
                                    </div>
                                    <p class="text-gray-400 text-sm mt-2">${ans.explanation || 'None'}</p>
                                </div>
                            `).join('')}
                        </div>
                        <div class="mt-6 text-center">
                            <button id="retry-incorrect-btn" class="bg-yellow-600 hover:bg-yellow-700 text-white py-3 px-8 rounded-xl font-semibold transition-all">
                                <i class="fas fa-redo mr-2"></i>Retry Incorrect Questions
                            </button>
                        </div>
                    </div>
                ` : ''}
                
                <div class="glass-effect rounded-2xl p-8 text-center">
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <button id="restart-quiz-btn" class="bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                            <i class="fas fa-play mr-2"></i>New Quiz
                        </button>
                        <button id="export-csv-btn" class="bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                            <i class="fas fa-download mr-2"></i>Export CSV
                        </button>
                        <button id="save-quiz-btn" class="bg-purple-600 hover:bg-purple-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                            <i class="fas fa-save mr-2"></i>Save Quiz
                        </button>
                        <button id="view-history-btn" class="bg-gray-600 hover:bg-gray-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                            <i class="fas fa-history mr-2"></i>View History
                        </button>
                    </div>
                </div>
            </div>`;
        addResultsEventListeners();
    }

    function renderHistoryView() {
        dom.views.history.innerHTML = `
            <div class="max-w-6xl mx-auto">
                <div class="glass-effect rounded-2xl p-8 mb-8">
                    <h2 class="text-4xl font-bold text-green-400 mb-8 text-center">
                        <i class="fas fa-history mr-3"></i>Quiz History
                    </h2>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div>
                            <label for="mode-filter" class="block mb-3 font-semibold text-green-400">
                                <i class="fas fa-filter mr-2"></i>Filter by Mode
                            </label>
                            <select id="mode-filter" class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none">
                                <option value="">All Modes</option>
                                <option value="ai">AI Generated</option>
                                <option value="manual">Manual Input</option>
                            </select>
                        </div>
                        <div>
                            <label for="date-filter" class="block mb-3 font-semibold text-green-400">
                                <i class="fas fa-calendar mr-2"></i>Filter by Date
                            </label>
                            <input type="date" id="date-filter" class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none">
                        </div>
                        <div class="flex items-end">
                            <button id="clear-filters-btn" class="w-full bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-xl font-semibold transition-all">
                                <i class="fas fa-times mr-2"></i>Clear Filters
                            </button>
                        </div>
                    </div>
                </div>
                
                <div id="history-list" class="space-y-6">
                    <div class="text-center py-8">
                        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-green-400 mx-auto mb-4"></div>
                        <p class="text-gray-400 text-lg">Loading quiz history...</p>
                    </div>
                </div>
                
                <div class="text-center mt-8">
                    <button id="back-to-setup-btn" class="bg-blue-600 hover:bg-blue-700 text-white py-3 px-8 rounded-xl font-semibold transition-all">
                        <i class="fas fa-arrow-left mr-2"></i>Back to Setup
                    </button>
                </div>
            </div>`;
        addHistoryEventListeners();
        loadHistory();
    }

    function renderSettingsView() {
        dom.views.settings.innerHTML = `
            <div class="max-w-5xl mx-auto">
                <div class="glass-effect rounded-2xl shadow-2xl p-8">
                    <h2 class="text-4xl font-bold mb-8 text-green-400 text-center">
                        <i class="fas fa-cog mr-3"></i>Settings & Configuration
                    </h2>
                    
                    <form id="settings-form" class="space-y-8">
                        <!-- Quiz Configuration -->
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <h3 class="text-2xl font-semibold mb-6 border-b border-gray-600 pb-3 text-yellow-400">
                                <i class="fas fa-sliders-h mr-2"></i>Quiz Configuration
                            </h3>
                            <div class="grid md:grid-cols-4 gap-6">
                                <div>
                                    <label for="total-questions" class="block mb-3 font-semibold text-green-400">Questions per Quiz</label>
                                    <input type="number" id="total-questions" min="1" max="50" class="w-full bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none" value="${state.settings.totalQuestions}">
                                </div>
                                <div>
                                    <label for="total-time" class="block mb-3 font-semibold text-green-400">Time Limit (minutes)</label>
                                    <input type="number" id="total-time" min="1" max="120" class="w-full bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none" value="${state.settings.totalTime}">
                                </div>
                                <div>
                                    <label for="default-difficulty" class="block mb-3 font-semibold text-green-400">Default Difficulty</label>
                                    <select id="default-difficulty" class="w-full bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none">
                                        <option value="easy" ${state.settings.difficulty === 'easy' ? 'selected' : ''}>Easy</option>
                                        <option value="medium" ${state.settings.difficulty === 'medium' ? 'selected' : ''}>Medium</option>
                                        <option value="hard" ${state.settings.difficulty === 'hard' ? 'selected' : ''}>Hard</option>
                                    </select>
                                </div>
                                <div>
                                    <label for="default-grade-level" class="block mb-3 font-semibold text-green-400">Default Grade Level</label>
                                    <select id="default-grade-level" class="w-full bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500 focus:outline-none">
                                        <option value="elementary" ${state.settings.gradeLevel === 'elementary' ? 'selected' : ''}>Elementary</option>
                                        <option value="middle school" ${state.settings.gradeLevel === 'middle school' ? 'selected' : ''}>Middle School</option>
                                        <option value="high school" ${state.settings.gradeLevel === 'high school' ? 'selected' : ''}>High School</option>
                                        <option value="college" ${state.settings.gradeLevel === 'college' ? 'selected' : ''}>College</option>
                                        <option value="graduate" ${state.settings.gradeLevel === 'graduate' ? 'selected' : ''}>Graduate</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- API Keys Configuration -->
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <h3 class="text-2xl font-semibold mb-6 border-b border-gray-600 pb-3 text-yellow-400">
                                <i class="fas fa-key mr-2"></i>API Keys
                            </h3>
                            <div class="space-y-6">
                                <div>
                                    <label for="gemini-key" class="block mb-3 font-semibold text-green-400">
                                        <i class="fab fa-google mr-2"></i>Google Gemini API Key
                                    </label>
                                    <div class="relative">
                                        <input type="password" id="gemini-key" placeholder="Enter your Gemini API Key" class="w-full bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 pr-12 focus:ring-2 focus:ring-green-500 focus:outline-none" value="${state.settings.apiKeys.gemini}">
                                        <button type="button" class="toggle-password absolute right-3 top-3 text-gray-400 hover:text-white" data-target="gemini-key">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                    </div>
                                </div>
                                <div>
                                    <label for="openai-key" class="block mb-3 font-semibold text-green-400">
                                        <i class="fas fa-brain mr-2"></i>OpenAI API Key
                                    </label>
                                    <div class="relative">
                                        <input type="password" id="openai-key" placeholder="Enter your OpenAI API Key" class="w-full bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 pr-12 focus:ring-2 focus:ring-green-500 focus:outline-none" value="${state.settings.apiKeys.openai}">
                                        <button type="button" class="toggle-password absolute right-3 top-3 text-gray-400 hover:text-white" data-target="openai-key">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                    </div>
                                </div>
                                <div>
                                    <label for="groq-key" class="block mb-3 font-semibold text-green-400">
                                        <i class="fas fa-bolt mr-2"></i>Groq API Key
                                    </label>
                                    <div class="relative">
                                        <input type="password" id="groq-key" placeholder="Enter your Groq API Key" class="w-full bg-gray-600 border border-gray-500 rounded-xl px-4 py-3 pr-12 focus:ring-2 focus:ring-green-500 focus:outline-none" value="${state.settings.apiKeys.groq}">
                                        <button type="button" class="toggle-password absolute right-3 top-3 text-gray-400 hover:text-white" data-target="groq-key">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Topics Management -->
                        <div class="bg-gray-700 p-6 rounded-xl">
                            <h3 class="text-2xl font-semibold mb-6 border-b border-gray-600 pb-3 text-yellow-400">
                                <i class="fas fa-book mr-2"></i>Topics & Sections Management
                            </h3>
                            <div id="sections-container" class="space-y-4 mb-6"></div>
                            <div class="text-center">
                                <button id="add-section-btn" type="button" class="bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-xl font-semibold transition-all">
                                    <i class="fas fa-plus mr-2"></i>Add New Section
                                </button>
                            </div>
                        </div>

                        <div class="text-center pt-6">
                            <button type="submit" class="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white py-4 px-12 rounded-xl text-xl font-bold transition-all transform hover:scale-105">
                                <i class="fas fa-save mr-3"></i>Save All Settings
                            </button>
                        </div>
                    </form>
                </div>
            </div>`;
        renderSections();
        addSettingsEventListeners();
    }

    function renderSections() {
        const container = document.getElementById('sections-container');
        if (!container) return;
        container.innerHTML = '';
        Object.entries(state.settings.topics).forEach(([section, topics]) => {
            const sectionEl = document.createElement('div');
            sectionEl.className = 'bg-gray-600 p-5 rounded-xl border border-gray-500';
            sectionEl.innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <input type="text" class="section-name bg-gray-700 border border-gray-500 rounded-lg px-4 py-2 text-lg font-semibold w-full mr-4 focus:ring-2 focus:ring-green-500 focus:outline-none" value="${section}" placeholder="Section name">
                    <button class="remove-section-btn text-red-400 hover:text-red-300 text-xl p-2" title="Remove section">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <textarea class="topic-input bg-gray-700 border border-gray-500 rounded-lg px-4 py-3 w-full text-sm focus:ring-2 focus:ring-green-500 focus:outline-none" rows="3" placeholder="Enter topics separated by commas (e.g., Algebra, Geometry, Calculus)">${topics.join(', ')}</textarea>`;
            container.appendChild(sectionEl);
        });
    }

    async function loadHistory() {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;
        
        historyList.innerHTML = `
            <div class="text-center py-8">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-green-400 mx-auto mb-4"></div>
                <p class="text-gray-400 text-lg">Loading quiz history...</p>
            </div>`;
        
        try {
            const params = new URLSearchParams();
            if (state.historyFilter.mode) params.append('mode', state.historyFilter.mode);
            if (state.historyFilter.date) params.append('date', state.historyFilter.date);
            
            const response = await fetch(`${API_BASE_URL}/history?${params.toString()}`);
            const responseText = await response.text();
            
            if (!response.ok) {
                let errorData;
                try {
                    errorData = JSON.parse(responseText);
                } catch {
                    errorData = { detail: responseText || 'Failed to load quiz history.' };
                }
                throw new Error(errorData.detail);
            }
            
            const quizzes = JSON.parse(responseText);
            
            historyList.innerHTML = quizzes.length ? quizzes.map(quiz => {
                const percentage = Math.round((quiz.score / quiz.total_questions) * 100);
                const badgeColor = percentage >= 80 ? 'bg-green-500' : percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500';
                
                return `
                    <div class="glass-effect rounded-xl p-6 hover:bg-gray-700 transition-all">
                        <div class="flex justify-between items-start mb-4">
                            <div class="flex-1">
                                <div class="flex items-center mb-2">
                                    <h3 class="text-xl font-bold text-green-400 mr-3">Quiz #${quiz.id}</h3>
                                    <span class="px-3 py-1 rounded-full text-xs font-semibold ${quiz.mode === 'ai' ? 'bg-blue-500' : 'bg-purple-500'} text-white">
                                        ${quiz.mode.toUpperCase()}
                                    </span>
                                    <span class="${badgeColor} text-white px-3 py-1 rounded-full text-sm font-bold ml-2">
                                        ${percentage}%
                                    </span>
                                </div>
                                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-400">
                                    <div><i class="fas fa-trophy mr-1"></i> ${quiz.score}/${quiz.total_questions}</div>
                                    <div><i class="fas fa-clock mr-1"></i> ${quiz.time_taken}</div>
                                    <div><i class="fas fa-calendar mr-1"></i> ${new Date(quiz.timestamp).toLocaleDateString()}</div>
                                    <div><i class="fas fa-tag mr-1"></i> ${quiz.grade_level || 'N/A'}</div>
                                </div>
                                <p class="text-gray-300 mt-2"><i class="fas fa-book mr-1"></i> ${quiz.sections}</p>
                            </div>
                            <button class="toggle-details-btn text-blue-400 hover:text-blue-300 p-2 transition-all" title="Toggle details">
                                <i class="fas fa-chevron-down text-xl"></i>
                            </button>
                        </div>
                        
                        <div class="details-container hidden">
                            <div class="border-t border-gray-600 pt-4 space-y-3 max-h-80 overflow-y-auto">
                                ${quiz.questions.map((q, i) => {
                                    const isCorrect = q.user_answer === q.correct_answer;
                                    return `
                                        <div class="p-4 rounded-lg ${isCorrect ? 'bg-green-900 border border-green-700' : 'bg-red-900 border border-red-700'}">
                                            <div class="flex items-start justify-between mb-2">
                                                <h4 class="font-semibold text-sm flex-1">${q.question_text}</h4>
                                                <span class="${isCorrect ? 'text-green-400' : 'text-red-400'} ml-2">
                                                    <i class="fas ${isCorrect ? 'fa-check' : 'fa-times'}"></i>
                                                </span>
                                            </div>
                                            <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                                                <p class="${isCorrect ? 'text-green-300' : 'text-red-300'}">
                                                    <strong>Your Answer:</strong> ${q.user_answer || 'None'}
                                                </p>
                                                <p class="text-green-300">
                                                    <strong>Correct:</strong> ${q.correct_answer}
                                                </p>
                                            </div>
                                            ${q.explanation ? `<p class="text-gray-400 text-xs mt-2">${q.explanation}</p>` : ''}
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            <div class="mt-4 flex justify-end space-x-2">
                                <button class="retry-quiz-btn bg-yellow-600 hover:bg-yellow-700 text-white py-2 px-4 rounded-lg text-sm font-semibold transition-all" data-quiz-id="${quiz.id}">
                                    <i class="fas fa-redo mr-1"></i>Retry Quiz
                                </button>
                                <button class="export-quiz-btn bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg text-sm font-semibold transition-all" data-quiz-id="${quiz.id}">
                                    <i class="fas fa-download mr-1"></i>Export
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('') : `
                <div class="glass-effect rounded-xl p-12 text-center">
                    <i class="fas fa-history text-6xl text-gray-500 mb-4"></i>
                    <h3 class="text-2xl font-semibold text-gray-400 mb-2">No Quiz History</h3>
                    <p class="text-gray-500">Complete some quizzes to see your history here!</p>
                </div>
            `;
            
            addHistoryDetailsEventListeners();
        } catch (error) {
            historyList.innerHTML = `
                <div class="glass-effect rounded-xl p-12 text-center">
                    <i class="fas fa-exclamation-triangle text-6xl text-red-400 mb-4"></i>
                    <h3 class="text-2xl font-semibold text-red-400 mb-2">Failed to Load History</h3>
                    <p class="text-gray-400">${error.message}</p>
                    <button onclick="loadHistory()" class="mt-4 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-semibold">
                        <i class="fas fa-refresh mr-2"></i>Try Again
                    </button>
                </div>
            `;
            showToast(error.message, true);
            logErrorToBackend(error, 'loadHistory', '');
        }
    }

    function addHistoryDetailsEventListeners() {
        const buttons = document.querySelectorAll('.toggle-details-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const details = btn.closest('.glass-effect').querySelector('.details-container');
                const icon = btn.querySelector('i');
                details.classList.toggle('hidden');
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            });
        });

        // Add retry quiz functionality
        document.querySelectorAll('.retry-quiz-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                showToast('Retry functionality coming soon!');
            });
        });

        // Add export quiz functionality
        document.querySelectorAll('.export-quiz-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                showToast('Export functionality coming soon!');
            });
        });
    }

    async function saveQuizResults() {
        const { score, questions, userAnswers, startTime, timeRemaining } = state.quiz;
        const timeTaken = `${Math.round((state.settings.totalTime * 60 - timeRemaining) / 60)}:${((state.settings.totalTime * 60 - timeRemaining) % 60).toString().padStart(2, '0')}`;
        const mode = document.getElementById('ai-mode-form')?.classList.contains('hidden') ? 'manual' : 'ai';
        const sections = [...new Set(questions.map(q => q.section))].join(',');
        
        const quizData = {
            score,
            total_questions: questions.length,
            time_taken: timeTaken,
            mode,
            sections,
            grade_level: state.settings.gradeLevel || 'high school',
            difficulty: state.settings.difficulty || 'medium',
            questions: userAnswers.map(ans => ({
                question_text: ans.question_text,
                options: ans.options,
                correct_answer: ans.correct_answer,
                explanation: ans.explanation || 'No explanation provided.',
                section: ans.section,
                topic: ans.topic,
                user_answer: ans.userAnswer
            }))
        };
        
        try {
            const response = await fetch(`${API_BASE_URL}/quiz`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(quizData)
            });
            const responseText = await response.text();
            if (!response.ok) {
                let errorData;
                try {
                    errorData = JSON.parse(responseText);
                } catch {
                    errorData = { detail: responseText || 'Failed to save quiz results.' };
                }
                throw new Error(errorData.detail);
            }
            showToast('Quiz results saved successfully! 💾');
        } catch (error) {
            showToast(error.message, true);
            logErrorToBackend(error, 'saveQuizResults', responseText);
        }
    }

    async function handleStartQuiz() {
        const isAiMode = !document.getElementById('ai-mode-form')?.classList.contains('hidden');
        showLoadingModal('Preparing your quiz...');
        
        try {
            let questions;
            if (isAiMode) {
                const provider = document.getElementById('ai-provider').value;
                const gradeLevel = document.getElementById('grade-level').value;
                const difficulty = document.getElementById('difficulty').value;
                const numQuestions = parseInt(document.getElementById('num-questions').value);
                const apiKey = state.settings.apiKeys[provider];
                
                if (!apiKey) throw new Error(`API Key for ${provider} is missing. Please add it in Settings.`);
                
                const response = await fetch(`${API_BASE_URL}/quiz/start`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        api_provider: provider,
                        api_key: apiKey,
                        num_questions: numQuestions,
                        grade_level: gradeLevel,
                        difficulty,
                        topics: Object.entries(state.settings.topics).flatMap(([section, topics]) => 
                            topics.map(topic => ({ section, topic }))
                        )
                    })
                });
                
                const responseText = await response.text();
                if (!response.ok) {
                    let errorData;
                    try {
                        errorData = JSON.parse(responseText);
                    } catch {
                        errorData = { detail: `Server error (status ${response.status}): ${responseText || 'No response body'}` };
                    }
                    throw new Error(errorData.detail);
                }
                
                try {
                    questions = JSON.parse(responseText);
                } catch (e) {
                    logErrorToBackend(new Error(`Invalid JSON response: ${responseText.substring(0, 500)}`), 'handleStartQuiz', responseText);
                    throw new Error(`Server returned invalid JSON: ${responseText.substring(0, 100)}...`);
                }
                
                if (!Array.isArray(questions) || questions.length === 0) {
                    throw new Error('No valid questions returned from server.');
                }
            } else {
                const manualInput = document.getElementById('manual-questions-input').value;
                if (!manualInput) throw new Error('Please paste questions in the manual input field.');
                
                try {
                    questions = JSON.parse(manualInput);
                    if (!Array.isArray(questions) || questions.length === 0) {
                        throw new Error('Invalid JSON format or no questions provided.');
                    }
                    
                    const requiredFields = ['question_text', 'options', 'correct_answer', 'explanation', 'section', 'topic'];
                    for (const q of questions) {
                        if (!requiredFields.every(field => field in q)) {
                            throw new Error(`Question missing required fields: ${JSON.stringify(q)}`);
                        }
                        if (!Array.isArray(q.options) || q.options.length !== 4) {
                            throw new Error(`Question has invalid options format: ${JSON.stringify(q.options)}`);
                        }
                    }
                } catch (e) {
                    throw new Error(`Invalid JSON or format: ${e.message}`);
                }
            }
            
            state.quiz = {
                questions,
                currentQuestionIndex: 0,
                score: 0,
                userAnswers: [],
                timeRemaining: state.settings.totalTime * 60,
                startTime: new Date()
            };
            
            hideLoadingModal();
            switchView('quiz');
        } catch (error) {
            hideLoadingModal();
            showToast(error.message, true);
            logErrorToBackend(error, 'handleStartQuiz', '');
        }
    }

    function addSetupEventListeners() {
        const aiToggle = document.getElementById('mode-toggle-ai');
        const manualToggle = document.getElementById('mode-toggle-manual');
        
        if (aiToggle) {
            aiToggle.addEventListener('click', e => {
                e.currentTarget.classList.add('bg-green-600', 'text-white');
                e.currentTarget.classList.remove('text-gray-300');
                manualToggle.classList.remove('bg-green-600', 'text-white');
                manualToggle.classList.add('text-gray-300');
                document.getElementById('ai-mode-form').classList.remove('hidden');
                document.getElementById('manual-mode-form').classList.add('hidden');
            });
        }
        
        if (manualToggle) {
            manualToggle.addEventListener('click', e => {
                e.currentTarget.classList.add('bg-green-600', 'text-white');
                e.currentTarget.classList.remove('text-gray-300');
                aiToggle.classList.remove('bg-green-600', 'text-white');
                aiToggle.classList.add('text-gray-300');
                document.getElementById('manual-mode-form').classList.remove('hidden');
                document.getElementById('ai-mode-form').classList.add('hidden');
            });
        }

        const generatePromptBtn = document.getElementById('generate-prompt-btn');
        if (generatePromptBtn) {
            generatePromptBtn.addEventListener('click', async () => {
                showLoadingModal('Generating prompt...');
                try {
                    const gradeLevel = document.getElementById('grade-level').value;
                    const difficulty = document.getElementById('difficulty').value;
                    const numQuestions = parseInt(document.getElementById('num-questions').value);
                    
                    const response = await fetch(`${API_BASE_URL}/quiz/generate-prompt`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            num_questions: numQuestions, 
                            topics: state.settings.topics,
                            grade_level: gradeLevel,
                            difficulty
                        })
                    });
                    
                    const responseText = await response.text();
                    if (!response.ok) {
                        let errorData;
                        try {
                            errorData = JSON.parse(responseText);
                        } catch {
                            errorData = { detail: `Server error (status ${response.status}): ${responseText || 'No response body'}` };
                        }
                        throw new Error(errorData.detail);
                    }
                    
                    const data = JSON.parse(responseText);
                    await navigator.clipboard.writeText(data.prompt);
                    showToast('Enhanced prompt copied to clipboard! 📋');
                } catch (error) {
                    showToast(error.message, true);
                    logErrorToBackend(error, 'generatePrompt', '');
                } finally {
                    hideLoadingModal();
                }
            });
        }

        const startQuizBtn = document.getElementById('start-quiz-btn');
        if (startQuizBtn) {
            startQuizBtn.addEventListener('click', handleStartQuiz);
        }
    }

    function addQuizEventListeners() {
        const optionsContainer = document.getElementById('options-container');
        if (optionsContainer) {
            optionsContainer.addEventListener('click', e => {
                const selectedCard = e.target.closest('.option-card');
                if (!selectedCard || selectedCard.classList.contains('disabled')) return;
                
                const q = state.quiz.questions[state.quiz.currentQuestionIndex];
                const isCorrect = selectedCard.dataset.option === q.correct_answer;
                
                if (isCorrect) state.quiz.score++;
                state.quiz.userAnswers.push({ ...q, userAnswer: selectedCard.dataset.option });
                
                document.querySelectorAll('.option-card').forEach(card => {
                    card.classList.add('disabled');
                    if (card.dataset.option === q.correct_answer) {
                        card.classList.add('correct');
                    } else if (card === selectedCard) {
                        card.classList.add('incorrect');
                    }
                });
                
                document.getElementById('explanation-text').textContent = q.explanation || 'No explanation provided.';
                document.getElementById('explanation-container').classList.remove('hidden');
                document.getElementById('next-question-btn').classList.remove('hidden');
            });
        }

        const nextButton = document.getElementById('next-question-btn');
        if (nextButton) {
            nextButton.addEventListener('click', () => {
                if (state.quiz.currentQuestionIndex < state.quiz.questions.length - 1) {
                    state.quiz.currentQuestionIndex++;
                    renderQuizView();
                } else {
                    endQuiz();
                }
            });
        }

        const endButton = document.getElementById('end-quiz-btn');
        if (endButton) {
            endButton.addEventListener('click', () => {
                if (confirm('Are you sure you want to end the quiz?')) endQuiz();
            });
        }

        const askAiButton = document.getElementById('ask-ai-btn');
        if (askAiButton) {
            askAiButton.addEventListener('click', async e => {
                const input = document.getElementById('ask-ai-input');
                const userQuery = input.value.trim();
                if (!userQuery) return;
                
                const apiKey = state.settings.apiKeys.gemini;
                if (!apiKey) {
                    showToast('Please set your Gemini API key in Settings.', true);
                    return;
                }
                
                const responseBox = document.getElementById('ai-response-box');
                responseBox.classList.remove('hidden');
                responseBox.textContent = 'Thinking...';
                e.currentTarget.disabled = true;
                
                try {
                    const response = await fetch(`${API_BASE_URL}/quiz/ask-ai`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            question_context: state.quiz.questions[state.quiz.currentQuestionIndex], 
                            user_query: userQuery, 
                            api_key: apiKey 
                        })
                    });
                    
                    const responseText = await response.text();
                    if (!response.ok) {
                        let errorData;
                        try {
                            errorData = JSON.parse(responseText);
                        } catch {
                            errorData = { detail: `Server error (status ${response.status}): ${responseText || 'No response body'}` };
                        }
                        throw new Error(errorData.detail);
                    }
                    
                    const data = JSON.parse(responseText);
                    responseBox.textContent = data.response;
                } catch (error) {
                    responseBox.textContent = `Error: ${error.message}`;
                    logErrorToBackend(error, 'askAI', '');
                } finally {
                    e.currentTarget.disabled = false;
                }
            });
        }
    }

    function addResultsEventListeners() {
        const restartButton = document.getElementById('restart-quiz-btn');
        if (restartButton) {
            restartButton.addEventListener('click', () => switchView('setup'));
        }

        const exportButton = document.getElementById('export-csv-btn');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                let csvContent = "data:text/csv;charset=utf-8,Question,Section,Topic,Your Answer,Correct Answer,Is Correct,Explanation\r\n";
                state.quiz.userAnswers.forEach(ans => {
                    csvContent += [
                        `"${ans.question_text.replace(/"/g, '""')}"`,
                        ans.section,
                        ans.topic,
                        ans.userAnswer,
                        ans.correct_answer,
                        ans.userAnswer === ans.correct_answer,
                        `"${ans.explanation.replace(/"/g, '""')}"`
                    ].join(',') + "\r\n";
                });
                
                const link = document.createElement("a");
                link.setAttribute("href", encodeURI(csvContent));
                link.setAttribute("download", `quiz_results_${new Date().toISOString().split('T')[0]}.csv`);
                document.body.appendChild(link);
                link.click();
                link.remove();
                showToast('Results exported successfully! 📊');
            });
        }

        const saveButton = document.getElementById('save-quiz-btn');
        if (saveButton) {
            saveButton.addEventListener('click', saveQuizResults);
        }

        const viewHistoryButton = document.getElementById('view-history-btn');
        if (viewHistoryButton) {
            viewHistoryButton.addEventListener('click', () => switchView('history'));
        }

        const retryBtn = document.getElementById('retry-incorrect-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                const incorrectQuestions = state.quiz.userAnswers.filter(ans => ans.userAnswer !== ans.correct_answer);
                if (incorrectQuestions.length > 0) {
                    state.quiz = {
                        questions: incorrectQuestions.map(ans => ({
                            question_text: ans.question_text,
                            options: ans.options,
                            correct_answer: ans.correct_answer,
                            explanation: ans.explanation,
                            section: ans.section,
                            topic: ans.topic
                        })),
                        currentQuestionIndex: 0,
                        score: 0,
                        userAnswers: [],
                        timeRemaining: state.settings.totalTime * 60,
                        startTime: new Date()
                    };
                    switchView('quiz');
                }
            });
        }
    }

    function addSettingsEventListeners() {
        const form = document.getElementById('settings-form');
        if (form) {
            form.addEventListener('submit', async e => {
                e.preventDefault();
                
                const totalQuestions = parseInt(document.getElementById('total-questions').value);
                const totalTime = parseInt(document.getElementById('total-time').value);
                const difficulty = document.getElementById('default-difficulty').value;
                const gradeLevel = document.getElementById('default-grade-level').value;
                
                if (totalQuestions < 1 || totalQuestions > 50) {
                    showToast('Questions must be between 1 and 50.', true);
                    return;
                }
                if (totalTime < 1 || totalTime > 120) {
                    showToast('Time limit must be between 1 and 120 minutes.', true);
                    return;
                }
                
                state.settings.totalQuestions = totalQuestions;
                state.settings.totalTime = totalTime;
                state.settings.difficulty = difficulty;
                state.settings.gradeLevel = gradeLevel;
                state.settings.apiKeys = {
                    gemini: document.getElementById('gemini-key').value.trim(),
                    openai: document.getElementById('openai-key').value.trim(),
                    groq: document.getElementById('groq-key').value.trim(),
                };
                
                try {
                    const response = await fetch(`${API_BASE_URL}/settings`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(state.settings)
                    });
                    
                    const responseText = await response.text();
                    if (!response.ok) {
                        let errorData;
                        try {
                            errorData = JSON.parse(responseText);
                        } catch {
                            errorData = { detail: responseText || 'Failed to save settings.' };
                        }
                        throw new Error(errorData.detail);
                    }
                    
                    saveState();
                    showToast('Settings saved successfully! ✅');
                } catch (error) {
                    showToast('Settings saved locally due to server error.', true);
                    logErrorToBackend(error, 'saveSettings', responseText);
                    saveState();
                }
            });
        }

        // Toggle password visibility
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.dataset.target;
                const input = document.getElementById(targetId);
                const icon = btn.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });

        const addSectionBtn = document.getElementById('add-section-btn');
        if (addSectionBtn) {
            addSectionBtn.addEventListener('click', () => {
                state.settings.topics[`New Section ${Object.keys(state.settings.topics).length + 1}`] = [];
                renderSections();
                saveState();
            });
        }

        const sectionsContainer = document.getElementById('sections-container');
        if (sectionsContainer) {
            sectionsContainer.addEventListener('change', e => {
                if (!e.target.matches('.section-name, .topic-input')) return;
                
                const newTopics = {};
                document.querySelectorAll('#sections-container > div').forEach(el => {
                    const sectionName = el.querySelector('.section-name').value.trim();
                    const topics = el.querySelector('.topic-input').value
                        .split(',')
                        .map(t => t.trim())
                        .filter(Boolean);
                    if (sectionName) newTopics[sectionName] = topics;
                });
                
                state.settings.topics = newTopics;
                saveState();
            });

            sectionsContainer.addEventListener('click', e => {
                const removeBtn = e.target.closest('.remove-section-btn');
                if (removeBtn) {
                    const sectionName = removeBtn.closest('.bg-gray-600').querySelector('.section-name').value;
                    delete state.settings.topics[sectionName];
                    renderSections();
                    saveState();
                }
            });
        }
    }

    function addHistoryEventListeners() {
        const modeFilter = document.getElementById('mode-filter');
        if (modeFilter) {
            modeFilter.addEventListener('change', e => {
                state.historyFilter.mode = e.target.value;
                loadHistory();
            });
        }

        const dateFilter = document.getElementById('date-filter');
        if (dateFilter) {
            dateFilter.addEventListener('change', e => {
                state.historyFilter.date = e.target.value;
                loadHistory();
            });
        }

        const clearFiltersBtn = document.getElementById('clear-filters-btn');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                state.historyFilter = { mode: '', date: '' };
                document.getElementById('mode-filter').value = '';
                document.getElementById('date-filter').value = '';
                loadHistory();
            });
        }

        const backButton = document.getElementById('back-to-setup-btn');
        if (backButton) {
            backButton.addEventListener('click', () => switchView('setup'));
        }
    }

    const loadState = () => {
        const savedSettings = localStorage.getItem('eduQuizSettings');
        if (savedSettings) {
            const parsed = JSON.parse(savedSettings);
            state.settings = { ...state.settings, ...parsed };
        }
    };

    const saveState = () => {
        localStorage.setItem('eduQuizSettings', JSON.stringify(state.settings));
    };

    const escapeHTML = str => String(str).replace(/[&<>'"]/g, tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[tag] || ''));

    const startTimer = () => {
        clearInterval(state.quiz.timerId);
        const timerEl = document.getElementById('quiz-timer');
        if (!timerEl) return;
        
        const update = () => {
            const minutes = Math.floor(state.quiz.timeRemaining / 60);
            const seconds = state.quiz.timeRemaining % 60;
            timerEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (state.quiz.timeRemaining <= 60) {
                timerEl.classList.add('text-red-400');
                timerEl.classList.remove('text-yellow-400');
            }
            
            if (state.quiz.timeRemaining-- <= 0) endQuiz();
        };
        
        update();
        state.quiz.timerId = setInterval(update, 1000);
    };

    const endQuiz = () => {
        clearInterval(state.quiz.timerId);
        switchView('results');
    };

    const init = () => {
        loadState();
        updateAppInfo(); // ✅ NEW: Update app title and footer
        
        dom.navLinks.forEach((link, index) => {
            link.addEventListener('click', e => {
                e.preventDefault();
                const viewName = link.dataset.view;
                switchView(viewName);
            });
        });
        
        switchView('setup');
    };
    
    init();
});