<template>
  <div class="p-8 max-w-2xl mx-auto space-y-8">
    <div class="flex items-center gap-4">
      <BackButton />
      <h1 class="text-3xl font-bold">Contact Support</h1>
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Send us a message</CardTitle>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="submitForm" class="space-y-6">
          <div class="grid gap-2">
            <label class="text-sm font-medium">Subject</label>
            <Input v-model="form.subject" placeholder="Brief description of your issue" required />
          </div>
          
          <div class="grid gap-2">
            <label class="text-sm font-medium">Priority</label>
            <select v-model="form.priority" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div class="grid gap-2">
            <label class="text-sm font-medium">Message</label>
            <textarea 
              v-model="form.message" 
              rows="5"
              class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Describe your issue in detail..."
              required
            ></textarea>
          </div>

          <Button type="submit" :disabled="isSubmitting" class="w-full">
            {{ isSubmitting ? 'Sending...' : 'Send Message' }}
          </Button>
        </form>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BackButton from '@/components-vue/navigation/BackButton.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Input from '@/components-vue/ui/Input.vue'
import Button from '@/components-vue/ui/Button.vue'

const router = useRouter()
const isSubmitting = ref(false)
const form = ref({
  subject: '',
  priority: 'medium',
  message: ''
})

const submitForm = async () => {
  isSubmitting.value = true
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1500))
  alert('Message sent successfully! Our team will get back to you shortly.')
  router.push('/help')
  isSubmitting.value = false
}
</script>
