<template>
  <div class="p-8 space-y-8">
    <div class="flex items-center gap-4">
      <BackButton />
      <h1 class="text-3xl font-bold">Help & Support</h1>
    </div>

    <div class="grid gap-6 md:grid-cols-2">
      <!-- FAQs -->
      <Card>
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="(faq, index) in faqs" :key="index" class="border-b pb-4 last:border-0 last:pb-0">
              <h3 class="font-medium mb-1">{{ faq.question }}</h3>
              <p class="text-sm text-muted-foreground">{{ faq.answer }}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Contact Support -->
      <Card>
        <CardHeader>
          <CardTitle>Contact Support</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <p class="text-muted-foreground">
            Can't find what you're looking for? Our support team is here to help you with any questions or issues.
          </p>
          <Button class="w-full" @click="router.push('/contact')">
            Contact Us
          </Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import BackButton from '@/components-vue/navigation/BackButton.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Button from '@/components-vue/ui/Button.vue'

const router = useRouter()

const faqs = [
  {
    question: 'How do I file my taxes?',
    answer: 'Start by clicking "New Filing" on the dashboard. Our AI assistant will guide you through the process step-by-step.'
  },
  {
    question: 'What documents do I need?',
    answer: 'You typically need your Form 16, bank statements, and investment proofs. You can upload these directly in the app.'
  },
  {
    question: 'How is my refund calculated?',
    answer: 'Refunds are calculated based on your total tax paid (TDS/Advance Tax) versus your actual tax liability after deductions.'
  }
]
</script>
