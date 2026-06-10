document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const fastaZone = document.getElementById('fastaZone');
    const fastaInput = document.getElementById('fastaInput');
    const fastaFileName = document.getElementById('fastaFileName');

    const snpsZone = document.getElementById('snpsZone');
    const snpsInput = document.getElementById('snpsInput');
    const snpsFileName = document.getElementById('snpsFileName');

    const lengthSlider = document.getElementById('primerLength');
    const lengthValue = document.getElementById('lengthValue');

    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingProgress = document.getElementById('loadingProgress');
    const errorMsg = document.getElementById('errorMessage');

    // Update Slider Value
    lengthSlider.addEventListener('input', (e) => {
        lengthValue.textContent = e.target.value;
    });

    // Setup Drag and Drop
    function setupDragAndDrop(zone, input, nameDisplay) {
        // Click to upload
        zone.addEventListener('click', () => input.click());

        // File selection handler
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateZoneState(zone, nameDisplay, e.target.files[0].name);
            }
        });

        // Drag events
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                input.files = e.dataTransfer.files;
                updateZoneState(zone, nameDisplay, e.dataTransfer.files[0].name);
            }
        });
    }

    function updateZoneState(zone, nameDisplay, fileName) {
        nameDisplay.textContent = fileName;
        zone.classList.add('has-file');
        
        // Handle icons
        const defaultIcon = zone.querySelector('.default-icon');
        const successIcon = zone.querySelector('.success-icon');
        
        if (defaultIcon && successIcon) {
            defaultIcon.classList.add('hidden');
            successIcon.classList.remove('hidden');
        }
    }

    setupDragAndDrop(fastaZone, fastaInput, fastaFileName);
    setupDragAndDrop(snpsZone, snpsInput, snpsFileName);

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validation
        if (!fastaInput.files.length || !snpsInput.files.length) {
            errorMsg.textContent = 'Please provide both FASTA and SNPs files.';
            return;
        }

        errorMsg.textContent = '';
        submitBtn.classList.add('loading');
        loadingProgress.classList.remove('hidden');
        submitBtn.disabled = true;

        const formData = new FormData();
        formData.append('fasta', fastaInput.files[0]);
        formData.append('snps', snpsInput.files[0]);
        formData.append('length', lengthSlider.value);

        try {
            const response = await fetch('/design', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error occurred');
            }

            // Handle file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'primers_output.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
        } catch (error) {
            errorMsg.textContent = error.message;
        } finally {
            submitBtn.classList.remove('loading');
            loadingProgress.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
});
