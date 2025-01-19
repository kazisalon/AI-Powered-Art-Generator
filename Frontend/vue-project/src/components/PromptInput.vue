<template>
	<div class="prompt-input">
		<label for="prompt" class="prompt-label">Describe your art:</label>
		<textarea
			id="prompt"
			v-model="userPrompt"
			placeholder="E.g., A futuristic city under a purple sky"
			class="prompt-textarea"
			@input="emitPrompt"
		></textarea>
	</div>
</template>

<script>
export default {
	name: "PromptInput",
	data() {
		return {
			userPrompt: "",
		};
	},
	methods: {
		emitPrompt() {
			this.$emit("update-prompt", this.userPrompt);
		},
	},
};
</script>

<style scoped>
.prompt-input {
	margin: 1rem 0;
	display: flex;
	flex-direction: column;
}
.prompt-label {
	font-size: 1rem;
	margin-bottom: 0.5rem;
	color: #555;
}
.prompt-textarea {
	width: 100%;
	min-height: 100px;
	padding: 0.75rem;
	font-size: 1rem;
	border: 1px solid #ccc;
	border-radius: 5px;
	resize: vertical;
	outline: none;
}
.prompt-textarea:focus {
	border-color: #007bff;
	box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}
</style>
