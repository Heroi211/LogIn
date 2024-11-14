<template>
    <v-footer>{{ currentYear }} Cod3bit. All rights reserved.</v-footer>
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
