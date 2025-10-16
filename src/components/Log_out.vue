<template>
    <div class="tooltip-container">
        <svg @click="logout" class="logout-container" style="margin: 2rem; height:2em"
            xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" title="Logout">
            <path
                d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z" />
        </svg>
        <span class="tooltip-text">Logout</span>
    </div>
</template>

<script>
import { useRouter } from 'vue-router';
import {ref} from 'vue';
export default {
    setup() {
        const router = useRouter();
        function logout() {
            localStorage.clear()
            window.location.href='www.eacsa.us/cdn-cgi/access/logout'
            // Redirect to login page
            router.push('/');
        }
        return {
            logout,
        };
    },
};

</script>



<style scoped>
.logout-container {
    position: fixed;
    bottom: 60px;
    /* Distance from the bottom of the screen */
    right: 25px;
    /* Distance from the right of the screen */
    cursor: pointer;
    color: #6e6e6e8f;
    /* Customize the icon color */
    z-index: 1000;
    /* Ensure it's on top of other elements */
    transition: color 0.3s ease;
}

.logout-container:hover {
    color: #3e3e3ece;
    /* Customize the icon color */
}

.tooltip-container {
    position: fixed;
    width: auto;
    bottom: 85px;
    /* Distance from the bottom of the screen */
    right: 120px;
    background: transparent;
}

.tooltip-text {
    visibility: hidden;
    width: 100px;
    color: #0000004b;
    text-align: center;
    border-radius: 5px;
    padding: 5px 0;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    /* Position above the icon */
    left: 50%;
    margin-left: -50px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip-container:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}
</style>
