<template>
  <header>
    <h1>Financeiro</h1>
    <button @click="logout">Logout</button>
  </header>

  <main>
    <Financeiro />
  </main>
</template>

<script>
import Financeiro from './components/criar_registro/Financeiro.vue'

export default {
  components: {
    Financeiro
  },
  methods: {
    logout() {
      console.log('Usuário deslogado')
    }
  }
}
</script>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

main {
  display: flex;
  flex-direction: column;
  gap: 30px;
}
</style>
