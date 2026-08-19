/**
 * ResumeIQ - Interactive Client Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    let selectedFile = null;
    let activeMode = 'upload'; // 'upload' | 'paste'
    let currentReport = null;
    let currentEmailDelivery = null;

    // Elements - Navigation & Status
    const engineStatusChip = document.getElementById('engineStatusChip');
    const engineStatusText = document.getElementById('engineStatusText');
    const openSettingsBtn = document.getElementById('openSettingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');

    // Elements - Form & Inputs
    const analyzeForm = document.getElementById('analyzeForm');
    const rolePills = document.querySelectorAll('.role-pill');
    const customRoleContainer = document.getElementById('customRoleContainer');
    const customRoleInput = document.getElementById('customRoleInput');
    const tabUpload = document.getElementById('tabUpload');
    const tabPaste = document.getElementById('tabPaste');
    const pdfDropzone = document.getElementById('pdfDropzone');
    const resumeFileInput = document.getElementById('resumeFileInput');
    const dropzonePrompt = document.getElementById('dropzonePrompt');
    const filePreviewCard = document.getElementById('filePreviewCard');
    const previewFileName = document.getElementById('previewFileName');
    const previewFileSize = document.getElementById('previewFileSize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const pasteAreaContainer = document.getElementById('pasteAreaContainer');
    const resumeTextInput = document.getElementById('resumeTextInput');
    const candidateEmailInput = document.getElementById('candidateEmailInput');
    const submitAnalyzeBtn = document.getElementById('submitAnalyzeBtn');
    const sampleButtons = document.querySelectorAll('.btn-sample');

    // Elements - Processing Overlay
    const uploadSection = document.getElementById('uploadSection');
    const processingCard = document.getElementById('processingCard');
    const processingTitle = document.getElementById('processingTitle');
    const processingStatus = document.getElementById('processingStatus');
    const progressBar = document.getElementById('progressBar');
    const pSteps = [
        document.getElementById('pStep1'),
        document.getElementById('pStep2'),
        document.getElementById('pStep3'),
        document.getElementById('pStep4'),
        document.getElementById('pStep5')
    ];

    // Elements - Results Section
    const resultsSection = document.getElementById('resultsSection');
    const emailStatusBanner = document.getElementById('emailStatusBanner');
    const emailBannerTitle = document.getElementById('emailBannerTitle');
    const emailBannerMsg = document.getElementById('emailBannerMsg');
    const previewEmailBtn = document.getElementById('previewEmailBtn');

    const resTargetRole = document.getElementById('resTargetRole');
    const resEngineUsed = document.getElementById('resEngineUsed');
    const resOverallScore = document.getElementById('resOverallScore');
    const scoreCircleProgress = document.getElementById('scoreCircleProgress');
    const resScoreGrade = document.getElementById('resScoreGrade');

    const resAtsScore = document.getElementById('resAtsScore');
    const meterAts = document.getElementById('meterAts');
    const resTechScore = document.getElementById('resTechScore');
    const meterTech = document.getElementById('meterTech');
    const resImpactScore = document.getElementById('resImpactScore');
    const meterImpact = document.getElementById('meterImpact');
    const resFormatScore = document.getElementById('resFormatScore');
    const meterFormat = document.getElementById('meterFormat');

    const resSummaryText = document.getElementById('resSummaryText');
    const resStrengthsList = document.getElementById('resStrengthsList');
    const resImprovementsList = document.getElementById('resImprovementsList');
    const resMissingKeywords = document.getElementById('resMissingKeywords');
    const resAtsVerdict = document.getElementById('resAtsVerdict');
    const resAtsDensity = document.getElementById('resAtsDensity');
    const resAtsTips = document.getElementById('resAtsTips');
    const resMissingSections = document.getElementById('resMissingSections');
    const resRewritesList = document.getElementById('resRewritesList');
    const resFinalRec = document.getElementById('resFinalRec');

    const resendEmailBtn = document.getElementById('resendEmailBtn');
    const printReportBtn = document.getElementById('printReportBtn');
    const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');

    // Email Preview Modal Elements
    const emailPreviewModal = document.getElementById('emailPreviewModal');
    const closeEmailPreviewBtn = document.getElementById('closeEmailPreviewBtn');
    const closeEmailPreviewFooterBtn = document.getElementById('closeEmailPreviewFooterBtn');
    const emailPreviewFrame = document.getElementById('emailPreviewFrame');
    const quickSendEmailInput = document.getElementById('quickSendEmailInput');
    const quickSendEmailBtn = document.getElementById('quickSendEmailBtn');

    // Init App
    fetchConfigStatus();

    // ==========================================
    // Role Selection Handling
    // ==========================================
    rolePills.forEach(pill => {
        pill.addEventListener('click', () => {
            rolePills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            const radio = pill.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                if (radio.value === 'Custom') {
                    customRoleContainer.classList.remove('hidden');
                    customRoleInput.focus();
                } else {
                    customRoleContainer.classList.add('hidden');
                }
            }
        });
    });

    // ==========================================
    // Mode Switching (Upload PDF vs. Paste Text)
    // ==========================================
    tabUpload.addEventListener('click', () => {
        activeMode = 'upload';
        tabUpload.classList.add('active');
        tabPaste.classList.remove('active');
        pdfDropzone.classList.remove('hidden');
        pasteAreaContainer.classList.add('hidden');
    });

    tabPaste.addEventListener('click', () => {
        activeMode = 'paste';
        tabPaste.classList.add('active');
        tabUpload.classList.remove('active');
        pdfDropzone.classList.add('hidden');
        pasteAreaContainer.classList.remove('hidden');
        resumeTextInput.focus();
    });

    // ==========================================
    // Drag & Drop File Handling
    // ==========================================
    pdfDropzone.addEventListener('click', (e) => {
        if (!e.target.closest('#removeFileBtn') && !selectedFile) {
            resumeFileInput.click();
        }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        pdfDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            pdfDropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        pdfDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            pdfDropzone.classList.remove('dragover');
        });
    });

    pdfDropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    resumeFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    function handleFileSelection(file) {
        if (!file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.txt')) {
            showToast('Please select a valid PDF or TXT file', 'error');
            return;
        }

        selectedFile = file;
        previewFileName.textContent = file.name;
        previewFileSize.textContent = formatBytes(file.size);
        
        dropzonePrompt.classList.add('hidden');
        filePreviewCard.classList.remove('hidden');
        showToast(`Loaded: ${file.name}`, 'info');
    }

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        resumeFileInput.value = '';
        filePreviewCard.classList.add('hidden');
        dropzonePrompt.classList.remove('hidden');
    });

    // ==========================================
    // Quick Sample Loaders
    // ==========================================
    sampleButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const roleId = btn.dataset.sample;
            try {
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading...';
                const resp = await fetch(`/api/sample-resume/${roleId}`);
                const data = await resp.json();

                // Switch to paste tab and inject
                tabPaste.click();
                resumeTextInput.value = data.text;
                
                // Select role
                rolePills.forEach(p => {
                    const r = p.querySelector('input[type="radio"]');
                    if (r && r.value === data.role) {
                        p.click();
                    }
                });

                showToast(`Loaded sample resume for ${data.role}`, 'success');
            } catch (err) {
                showToast('Failed to load sample resume.', 'error');
            } finally {
                btn.innerHTML = roleId === 'backend' ? 'Backend Dev' : roleId === 'frontend' ? 'Frontend Dev' : 'HR Manager';
            }
        });
    });

    // ==========================================
    // Submit & Analysis Handler
    // ==========================================
    analyzeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validation
        if (activeMode === 'upload' && !selectedFile) {
            showToast('Please upload a PDF resume file first.', 'error');
            return;
        }
        if (activeMode === 'paste' && !resumeTextInput.value.trim()) {
            showToast('Please paste your resume text to analyze.', 'error');
            return;
        }

        // Gather form data
        const formData = new FormData();
        const selectedRadio = document.querySelector('input[name="target_role"]:checked');
        const roleVal = selectedRadio ? selectedRadio.value : 'General / Best Practices';

        if (roleVal === 'Custom') {
            const customRole = customRoleInput.value.trim();
            if (!customRole) {
                showToast('Please enter your custom target role.', 'error');
                customRoleInput.focus();
                return;
            }
            formData.append('role', 'Other');
            formData.append('custom_role', customRole);
        } else {
            formData.append('role', roleVal);
        }

        if (activeMode === 'upload') {
            try {
                const base64Data = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = error => reject(error);
                    reader.readAsDataURL(selectedFile);
                });
                formData.append('pdf_base64', base64Data);
            } catch (err) {
                formData.append('resume', selectedFile);
            }
        } else {
            formData.append('text', resumeTextInput.value.trim());
        }

        const email = candidateEmailInput.value.trim();
        if (email) {
            formData.append('email', email);
        }

        // Show Processing Screen
        startProcessingAnimation(roleVal === 'Custom' ? customRoleInput.value.trim() : roleVal);

        try {
            const resp = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await resp.json();

            if (!resp.ok || !result.success) {
                throw new Error(result.error || 'Failed to analyze resume.');
            }

            // Finish processing animation and show dashboard
            finishProcessingAnimation(() => {
                currentReport = result.report;
                currentEmailDelivery = result.email_delivery;
                displayResults(result);
            });

        } catch (err) {
            stopProcessingAnimation();
            showToast(err.message, 'error');
        }
    });

    // ==========================================
    // Processing Animation Engine
    // ==========================================
    let progressInterval = null;

    function startProcessingAnimation(targetRole) {
        uploadSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        processingCard.classList.remove('hidden');

        progressBar.style.width = '10%';
        pSteps.forEach((s, i) => {
            s.className = 'step-item';
            if (i === 0) s.classList.add('active');
        });

        const statusStages = [
            { pct: 25, title: 'Extracting Resume Text...', desc: 'Parsing structural sections and metadata...', stepIdx: 0 },
            { pct: 50, title: `Evaluating for ${targetRole}...`, desc: 'Checking technical keywords & core competencies...', stepIdx: 1 },
            { pct: 75, title: 'Running ATS Scanner...', desc: 'Calculating keyword density & readability...', stepIdx: 2 },
            { pct: 90, title: 'Generating Bullet Rewrites...', desc: 'Applying XYZ formula (Accomplished X by Y through Z)...', stepIdx: 3 },
            { pct: 98, title: 'Finalizing Report...', desc: 'Synthesizing scores and preparing email delivery...', stepIdx: 4 }
        ];

        let stageIdx = 0;
        progressInterval = setInterval(() => {
            if (stageIdx < statusStages.length) {
                const stage = statusStages[stageIdx];
                progressBar.style.width = `${stage.pct}%`;
                processingTitle.textContent = stage.title;
                processingStatus.textContent = stage.desc;

                pSteps.forEach((s, idx) => {
                    if (idx < stage.stepIdx) {
                        s.className = 'step-item done';
                    } else if (idx === stage.stepIdx) {
                        s.className = 'step-item active';
                    } else {
                        s.className = 'step-item';
                    }
                });

                stageIdx++;
            }
        }, 800);
    }

    function finishProcessingAnimation(callback) {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        pSteps.forEach(s => s.className = 'step-item done');
        processingTitle.textContent = 'Analysis Complete!';
        processingStatus.textContent = 'Rendering dashboard insights...';

        setTimeout(() => {
            processingCard.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            if (callback) callback();
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 500);
    }

    function stopProcessingAnimation() {
        clearInterval(progressInterval);
        processingCard.classList.add('hidden');
        uploadSection.classList.remove('hidden');
    }

    // ==========================================
    // Render Results Dashboard
    // ==========================================
    function displayResults(data) {
        const report = data.report;
        const meta = data.meta || {};
        const emailDelivery = data.email_delivery || {};

        // Email Banner Status
        if (emailDelivery.sent) {
            emailStatusBanner.className = 'email-banner';
            emailBannerTitle.textContent = '📩 Report Sent to Your Inbox!';
            emailBannerMsg.textContent = emailDelivery.message;
        } else if (emailDelivery.simulated && meta.candidate_email) {
            emailStatusBanner.className = 'email-banner';
            emailBannerTitle.textContent = '📋 Report Preview Ready';
            emailBannerMsg.textContent = emailDelivery.message;
        } else {
            emailStatusBanner.className = 'email-banner';
            emailBannerTitle.textContent = '💡 Audit Completed Successfully';
            emailBannerMsg.textContent = 'Explore your detailed scores, ATS feedback, and recommended bullet rewrites below.';
        }

        // Header Meta
        resTargetRole.textContent = report.target_role || 'General';
        resEngineUsed.textContent = report.engine_used || 'AI Engine';

        // Overall Score Gauge Animation
        const score = report.overall_score || 0;
        resOverallScore.textContent = score;
        resScoreGrade.textContent = `${report.score_grade || 'Strong'} Match`;

        // Color coding
        let scoreStrokeColor = '#6366f1';
        if (score >= 85) {
            scoreStrokeColor = '#10b981';
            resScoreGrade.style.background = 'rgba(16, 185, 129, 0.15)';
            resScoreGrade.style.color = '#34d399';
        } else if (score >= 70) {
            scoreStrokeColor = '#6366f1';
            resScoreGrade.style.background = 'rgba(99, 102, 241, 0.15)';
            resScoreGrade.style.color = '#a5b4fc';
        } else if (score >= 55) {
            scoreStrokeColor = '#f59e0b';
            resScoreGrade.style.background = 'rgba(245, 158, 11, 0.15)';
            resScoreGrade.style.color = '#fcd34d';
        } else {
            scoreStrokeColor = '#f43f5e';
            resScoreGrade.style.background = 'rgba(244, 63, 94, 0.15)';
            resScoreGrade.style.color = '#fda4af';
        }

        // Animate Circle
        scoreCircleProgress.style.stroke = scoreStrokeColor;
        const circumference = 2 * Math.PI * 70; // ~439.8
        const offset = circumference - (score / 100) * circumference;
        setTimeout(() => {
            scoreCircleProgress.style.strokeDashoffset = offset;
        }, 100);

        // Sub-Scores
        const sub = report.sub_scores || {};
        const ats = report.ats_score || sub.formatting_structure || 75;
        const tech = sub.technical_skills || 80;
        const impact = sub.experience_impact || 70;
        const format = sub.formatting_structure || 85;

        resAtsScore.textContent = `${ats}%`;
        resTechScore.textContent = `${tech}%`;
        resImpactScore.textContent = `${impact}%`;
        resFormatScore.textContent = `${format}%`;

        setTimeout(() => {
            meterAts.style.width = `${ats}%`;
            meterTech.style.width = `${tech}%`;
            meterImpact.style.width = `${impact}%`;
            meterFormat.style.width = `${format}%`;
        }, 150);

        // Executive Summary
        resSummaryText.textContent = report.summary || '';

        // Strengths
        resStrengthsList.innerHTML = '';
        (report.strengths || []).forEach(s => {
            const el = document.createElement('div');
            el.className = 'strength-item';
            el.innerHTML = `
                <div class="strength-title"><i class="fa-solid fa-circle-check"></i> ${escapeHtml(s.title || '')}</div>
                <div class="strength-desc">${escapeHtml(s.description || '')}</div>
            `;
            resStrengthsList.appendChild(el);
        });

        // Improvements
        resImprovementsList.innerHTML = '';
        (report.improvement_suggestions || []).forEach(imp => {
            const el = document.createElement('div');
            el.className = 'improvement-item';
            el.innerHTML = `
                <div class="imp-category">${escapeHtml(imp.category || 'Improvement')}</div>
                <div class="imp-issue"><strong>Gap:</strong> ${escapeHtml(imp.issue || '')}</div>
                <div class="imp-action"><strong>Action:</strong> ${escapeHtml(imp.action || '')}</div>
            `;
            resImprovementsList.appendChild(el);
        });

        // Missing Keywords Cloud
        resMissingKeywords.innerHTML = '';
        (report.missing_skills || []).forEach(kw => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag';
            tag.innerHTML = `<i class="fa-solid fa-plus"></i> ${escapeHtml(kw)}`;
            resMissingKeywords.appendChild(tag);
        });

        // ATS Feedback
        const atsFeedback = report.ats_feedback || {};
        resAtsVerdict.textContent = atsFeedback.verdict || 'Pass';
        resAtsDensity.textContent = atsFeedback.keyword_density || atsFeedback.file_formatting_check || 'Readable structure detected.';
        
        resAtsTips.innerHTML = '';
        (atsFeedback.tips || []).forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            resAtsTips.appendChild(li);
        });

        // Missing Sections
        resMissingSections.innerHTML = '';
        (report.missing_sections || []).forEach(sec => {
            const li = document.createElement('li');
            li.className = 'missing-sec-item';
            li.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${escapeHtml(sec)}`;
            resMissingSections.appendChild(li);
        });

        // Bullet Rewrites
        resRewritesList.innerHTML = '';
        (report.bullet_rewrites || []).forEach(rw => {
            const card = document.createElement('div');
            card.className = 'rewrite-card';
            card.innerHTML = `
                <div class="rewrite-row">
                    <span class="rewrite-label label-original">❌ Original Bullet Point:</span>
                    <div class="rewrite-original-text">${escapeHtml(rw.original || '')}</div>
                </div>
                <div class="rewrite-row">
                    <span class="rewrite-label label-improved">✨ High-Converting Rewrite:</span>
                    <div class="rewrite-improved-text">${escapeHtml(rw.improved || '')}</div>
                </div>
                <div class="rewrite-reason"><strong>Why this works:</strong> ${escapeHtml(rw.reason || '')}</div>
            `;
            resRewritesList.appendChild(card);
        });

        // Final Recommendation
        resFinalRec.textContent = report.final_recommendation || '';
    }

    // ==========================================
    // Email Preview Modal
    // ==========================================
    previewEmailBtn.addEventListener('click', () => {
        if (!currentEmailDelivery || !currentEmailDelivery.rendered_html) {
            showToast('Email preview is not available.', 'error');
            return;
        }

        const doc = emailPreviewFrame.contentWindow.document;
        doc.open();
        doc.write(currentEmailDelivery.rendered_html);
        doc.close();

        if (candidateEmailInput.value.trim()) {
            quickSendEmailInput.value = candidateEmailInput.value.trim();
        }

        emailPreviewModal.classList.remove('hidden');
    });

    closeEmailPreviewBtn.addEventListener('click', () => emailPreviewModal.classList.add('hidden'));
    closeEmailPreviewFooterBtn.addEventListener('click', () => emailPreviewModal.classList.add('hidden'));

    quickSendEmailBtn.addEventListener('click', async () => {
        const email = quickSendEmailInput.value.trim();
        if (!email) {
            showToast('Please enter an email address.', 'error');
            return;
        }
        await triggerEmailSend(email);
    });

    resendEmailBtn.addEventListener('click', async () => {
        const email = candidateEmailInput.value.trim() || prompt('Enter recipient email address:');
        if (email) {
            await triggerEmailSend(email);
        }
    });

    async function triggerEmailSend(email) {
        if (!currentReport) {
            showToast('No report available to send.', 'error');
            return;
        }
        try {
            showToast(`Dispatching report to ${email}...`, 'info');
            const resp = await fetch('/api/send-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, report: currentReport })
            });
            const data = await resp.json();
            if (data.delivery && data.delivery.sent) {
                showToast(`Report sent to ${email}!`, 'success');
                emailStatusBanner.className = 'email-banner';
                emailBannerTitle.textContent = '📩 Report Sent to Your Inbox!';
                emailBannerMsg.textContent = data.delivery.message;
            } else {
                showToast(data.delivery?.message || 'Email delivery previewed.', 'info');
            }
        } catch (err) {
            showToast('Failed to trigger email delivery.', 'error');
        }
    }

    // ==========================================
    // Print / Reset
    // ==========================================
    printReportBtn.addEventListener('click', () => {
        window.print();
    });

    analyzeAnotherBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        uploadSection.scrollIntoView({ behavior: 'smooth' });
    });

    // ==========================================
    // Settings & Configuration Modal
    // ==========================================
    openSettingsBtn.addEventListener('click', () => {
        settingsModal.classList.remove('hidden');
    });

    closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    cancelSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));

    saveSettingsBtn.addEventListener('click', async () => {
        const payload = {
            openai_key: document.getElementById('settingOpenaiKey').value.trim(),
            gemini_key: document.getElementById('settingGeminiKey').value.trim(),
            smtp_email: document.getElementById('settingSmtpEmail').value.trim(),
            smtp_password: document.getElementById('settingSmtpPass').value.trim()
        };

        try {
            const resp = await fetch('/api/save-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (data.success) {
                showToast('Settings saved successfully!', 'success');
                settingsModal.classList.add('hidden');
                fetchConfigStatus();
            }
        } catch (e) {
            showToast('Failed to save settings.', 'error');
        }
    });

    async function fetchConfigStatus() {
        try {
            const resp = await fetch('/api/config-status');
            const data = await resp.json();
            if (data.openai_configured) {
                engineStatusText.textContent = 'OpenAI GPT-4o Active';
            } else if (data.gemini_configured) {
                engineStatusText.textContent = 'Gemini 1.5 Active';
            } else {
                engineStatusText.textContent = 'Heuristic AI Active';
            }
        } catch (e) {
            console.log('Status check failed');
        }
    }

    // ==========================================
    // Utilities
    // ==========================================
    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-circle-check';
        if (type === 'error') icon = 'fa-circle-exclamation';

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});
