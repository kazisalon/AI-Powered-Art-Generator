<template>
	<header class="header">
		<nav class="nav">
			<div class="nav-container">
				<!-- Logo/Brand -->
				<div class="logo">
					<span>Logo</span>
				</div>

				<!-- Navigation Links -->
				<div class="nav-links">
					<router-link
						to="/"
						class="nav-link"
						:class="{ active: currentRoute === '/' }"
					>
						Home
					</router-link>
					<router-link
						to="/contact"
						class="nav-link"
						:class="{ active: currentRoute === '/contact' }"
					>
						Contact Us
					</router-link>
					<router-link
						to="/services"
						class="nav-link"
						:class="{ active: currentRoute === '/services' }"
					>
						Services
					</router-link>
				</div>
			</div>
		</nav>
	</header>
</template>

<script>
export default {
	name: "HeaderNav",
	computed: {
		currentRoute() {
			return this.$route.path;
		},
	},
};
</script>

<style scoped>
.header {
	background-color: white;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav {
	padding: 0 2rem;
}

.nav-container {
	max-width: 1200px;
	margin: 0 auto;
	height: 64px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.logo {
	font-size: 1.5rem;
	font-weight: bold;
	color: #333;
}

.nav-links {
	display: flex;
	gap: 2rem;
}

.nav-link {
	color: #666;
	text-decoration: none;
	font-size: 0.875rem;
	padding: 0.5rem;
	border-radius: 0.375rem;
	transition: color 0.2s, background-color 0.2s;
}

.nav-link:hover {
	color: #333;
	background-color: rgba(0, 0, 0, 0.05);
}

.nav-link.active {
	color: #333;
	font-weight: 500;
}

/* Responsive Design */
@media (max-width: 640px) {
	.nav {
		padding: 0 1rem;
	}

	.nav-links {
		gap: 1rem;
	}
}
</style>
