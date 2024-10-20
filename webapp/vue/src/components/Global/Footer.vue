<template>
    <footer class="footer">
        <div class="container">
            <p>&copy; {{ currentYear }} Cod3bit. All rights reserved.</p>
        </div>
    </footer>
</template>

<script>
export default {
    name: 'Footer',
    data() {
        return {
            currentYear: new Date().getFullYear()
        };
    }
};
</script>

