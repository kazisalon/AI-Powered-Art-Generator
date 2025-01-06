<!-- App.vue -->
<template>
	<div class="container">
		<div class="card">
			<h1>AI Art Generator</h1>

			<!-- Form Section -->
			<div class="form-group">
				<label>Description</label>
				<input
					v-model="prompt"
					type="text"
					placeholder="Describe your desired artwork..."
				/>
			</div>

			<div class="form-group">
				<label>Art Style</label>
				<select v-model="style">
					<option value="realistic">Realistic</option>
					<option value="abstract">Abstract</option>
					<option value="impressionist">Impressionist</option>
					<option value="pixel">Pixel Art</option>
				</select>
			</div>

			<button
				@click="generateArt"
				:disabled="isLoading || !prompt"
				class="generate-btn"
			>
				<div v-if="isLoading" class="spinner"></div>
				<span>{{ isLoading ? "Generating..." : "Generate Art" }}</span>
			</button>

			<!-- Generated Image Section -->
			<div v-if="generatedImage" class="result-section">
				<img
					:src="generatedImage"
					alt="Generated artwork"
					class="generated-image"
				/>

				<div class="action-buttons">
					<button @click="downloadImage" class="action-btn">Download</button>
					<button @click="generateArt" class="action-btn">Regenerate</button>
				</div>
			</div>

			<!-- Error Message -->
			<div v-if="error" class="error-message">
				{{ error }}
			</div>
		</div>
	</div>
</template>

<script>
export default {
	data() {
		return {
			prompt: "",
			style: "realistic",
			isLoading: false,
			generatedImage: null,
			error: null,
		};
	},
	methods: {
		async generateArt() {
			this.isLoading = true;
			this.error = null;

			try {
				const response = await fetch("http://localhost:8000/api/generate", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						prompt: this.prompt,
						style: this.style,
					}),
				});

				if (!response.ok) {
					throw new Error("Failed to generate image");
				}

				const data = await response.json();
				this.generatedImage = `data:image/jpeg;base64,${data.image}`;
			} catch (err) {
				this.error = "Error generating image. Please try again.";
				console.error("Error:", err);
			} finally {
				this.isLoading = false;
			}
		},
		downloadImage() {
			if (!this.generatedImage) return;

			const link = document.createElement("a");
			link.href = this.generatedImage;
			link.download = "generated-art.png";
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		},
	},
};
</script>

<style>
* {
	margin: 0;
	padding: 0;
	box-sizing: border-box;
}

body {
	font-family: Arial, sans-serif;
	background-color: #f0f2f5;
	line-height: 1.6;
}

.container {
	min-height: 100vh;
	padding: 2rem;
	display: flex;
	justify-content: center;
	align-items: flex-start;
}

.card {
	background: white;
	padding: 2rem;
	border-radius: 12px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	width: 100%;
	max-width: 600px;
}

h1 {
	text-align: center;
	color: #1a1a1a;
	margin-bottom: 2rem;
	font-size: 2rem;
}

.form-group {
	margin-bottom: 1.5rem;
}

label {
	display: block;
	margin-bottom: 0.5rem;
	color: #4a4a4a;
	font-weight: bold;
}

input,
select {
	width: 100%;
	padding: 0.75rem;
	border: 1px solid #ddd;
	border-radius: 6px;
	font-size: 1rem;
}

input:focus,
select:focus {
	outline: none;
	border-color: #4a90e2;
	box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.generate-btn {
	width: 100%;
	padding: 0.75rem;
	background-color: #4a90e2;
	color: white;
	border: none;
	border-radius: 6px;
	font-size: 1rem;
	cursor: pointer;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 0.5rem;
}

.generate-btn:hover {
	background-color: #357abd;
}

.generate-btn:disabled {
	background-color: #ccc;
	cursor: not-allowed;
}

.spinner {
	width: 20px;
	height: 20px;
	border: 3px solid #ffffff;
	border-top: 3px solid transparent;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

@keyframes spin {
	0% {
		transform: rotate(0deg);
	}

	100% {
		transform: rotate(360deg);
	}
}

.result-section {
	margin-top: 1.5rem;
}

.generated-image {
	width: 100%;
	border-radius: 8px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-buttons {
	display: flex;
	gap: 1rem;
	margin-top: 1rem;
}

.action-btn {
	flex: 1;
	padding: 0.75rem;
	background-color: white;
	color: #4a90e2;
	border: 1px solid #4a90e2;
	border-radius: 6px;
	cursor: pointer;
	font-size: 1rem;
}

.action-btn:hover {
	background-color: #f5f9ff;
}

.error-message {
	margin-top: 1rem;
	color: #dc3545;
	text-align: center;
}

@media (max-width: 480px) {
	.container {
		padding: 1rem;
	}

	.card {
		padding: 1rem;
	}

	.action-buttons {
		flex-direction: column;
	}
}
</style>
