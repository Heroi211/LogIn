<template>
    <div>
        <Navbar />
        <main>
            <h1>Welcome to HomeView</h1>
        </main>
        <Footer />
    </div>
</template>
<script>
import Footer from '@/components/Global/Footer.vue';
import Navbar from '@/components/Global/Navbar.vue';

export default {
    name: 'HomeView',
    components: {
        Navbar,
        Footer
    }
};
</script>