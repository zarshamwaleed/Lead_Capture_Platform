// Lead Capture Platform - Embeddable Widget
(function() {
    'use strict';

    // Get widget ID from script URL
    function getWidgetId() {
        const scripts = document.getElementsByTagName('script');
        const currentScript = scripts[scripts.length - 1];
        const src = currentScript.src;
        const match = src.match(/[?&]id=([^&]+)/);
        return match ? match[1] : null;
    }

    // Get widget configuration
    async function getWidgetConfig(widgetId) {
        const response = await fetch(http://localhost:8000/api/widgets/public//config);
        if (!response.ok) {
            throw new Error('Failed to load widget configuration');
        }
        return response.json();
    }

    // Render the widget
    function renderWidget(config) {
        // Create container
        const container = document.createElement('div');
        container.id = 'lead-capture-widget';
        container.style.cssText = 
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            width: 100%;
            font-family: Arial, sans-serif;
        ;

        // Create widget card
        const card = document.createElement('div');
        card.style.cssText = 
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            padding: 24px;
            
        ;

        // Title
        const title = document.createElement('h3');
        title.textContent = config.title;
        title.style.cssText = 'margin: 0 0 8px 0; font-size: 18px; font-weight: 600;';
        card.appendChild(title);

        // Description
        if (config.description) {
            const desc = document.createElement('p');
            desc.textContent = config.description;
            desc.style.cssText = 'margin: 0 0 16px 0; font-size: 14px; opacity: 0.8;';
            card.appendChild(desc);
        }

        // Form
        const form = document.createElement('form');
        form.id = 'lead-capture-form';

        // Fields
        config.fields.forEach(fieldName => {
            const fieldContainer = document.createElement('div');
            fieldContainer.style.cssText = 'margin-bottom: 12px;';

            const label = document.createElement('label');
            label.textContent = fieldName.charAt(0).toUpperCase() + fieldName.slice(1);
            label.style.cssText = 'display: block; margin-bottom: 4px; font-size: 14px; font-weight: 500;';
            fieldContainer.appendChild(label);

            let input;
            if (fieldName === 'message' || fieldName === 'comments') {
                input = document.createElement('textarea');
                input.rows = 3;
                input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; resize: vertical;';
            } else {
                input = document.createElement('input');
                input.type = fieldName === 'email' ? 'email' : 'text';
                input.style.cssText = 'width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;';
            }
            
            input.id = ield-;
            input.name = fieldName;
            input.placeholder = Enter ;
            input.required = true;
            
            // Add honeypot field for spam protection (hidden)
            if (fieldName === 'website') {
                input.style.display = 'none';
            }
            
            fieldContainer.appendChild(input);
            form.appendChild(fieldContainer);
        });

        // Add honeypot field (hidden)
        const honeypotContainer = document.createElement('div');
        honeypotContainer.style.display = 'none';
        const honeypotInput = document.createElement('input');
        honeypotInput.type = 'text';
        honeypotInput.name = 'website';
        honeypotInput.id = 'honeypot';
        honeypotInput.value = '';
        honeypotContainer.appendChild(honeypotInput);
        form.appendChild(honeypotContainer);

        // Submit button
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = config.button_text || 'Submit';
        submitButton.style.cssText = 
            width: 100%;
            padding: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.3s;
        ;
        submitButton.onmouseover = () => { submitButton.style.background = '#0056b3'; };
        submitButton.onmouseout = () => { submitButton.style.background = '#007bff'; };
        form.appendChild(submitButton);

        // Status message
        const status = document.createElement('div');
        status.id = 'widget-status';
        status.style.cssText = 'margin-top: 12px; text-align: center; font-size: 14px;';
        form.appendChild(status);

        card.appendChild(form);

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '×';
        closeBtn.style.cssText = 
            position: absolute;
            top: 8px;
            right: 12px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #999;
        ;
        closeBtn.onclick = () => { container.style.display = 'none'; };
        card.style.position = 'relative';
        card.appendChild(closeBtn);

        container.appendChild(card);
        document.body.appendChild(container);

        // Handle form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const statusDiv = document.getElementById('widget-status');
            
            // Check honeypot
            const honeypot = document.getElementById('honeypot');
            if (honeypot && honeypot.value) {
                statusDiv.textContent = 'Submission rejected (spam)';
                statusDiv.style.color = 'red';
                return;
            }

            // Collect form data
            const formData = {};
            config.fields.forEach(fieldName => {
                const input = document.getElementById(ield-);
                if (input) {
                    formData[fieldName] = input.value;
                }
            });

            try {
                submitBtn.textContent = 'Submitting...';
                submitBtn.disabled = true;
                statusDiv.textContent = '';

                const response = await fetch('http://localhost:8000/api/public/submissions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        widget_id: config.id,
                        data: formData
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    statusDiv.textContent = '✅ ' + (result.message || 'Submission successful!');
                    statusDiv.style.color = 'green';
                    form.reset();
                } else {
                    statusDiv.textContent = '❌ ' + (result.detail || 'Submission failed');
                    statusDiv.style.color = 'red';
                }
            } catch (error) {
                statusDiv.textContent = '❌ Error submitting form';
                statusDiv.style.color = 'red';
                console.error('Submission error:', error);
            } finally {
                submitBtn.textContent = config.button_text || 'Submit';
                submitBtn.disabled = false;
            }
        });
    }

    // Initialize widget
    async function initWidget() {
        try {
            const widgetId = getWidgetId();
            if (!widgetId) {
                console.error('Widget ID not found in script URL');
                return;
            }

            const config = await getWidgetConfig(widgetId);
            renderWidget(config);
        } catch (error) {
            console.error('Widget initialization error:', error);
        }
    }

    // Load widget when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
})();
