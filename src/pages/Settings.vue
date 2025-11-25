<template>
  <div class="p-8 space-y-8">
    <div class="flex items-center gap-4">
      <BackButton />
      <h1 class="text-3xl font-bold">Settings</h1>
    </div>

    <div class="flex flex-col md:flex-row gap-8">
      <!-- Sidebar Navigation for Settings -->
      <div class="w-full md:w-64 space-y-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="cn(
            'w-full text-left px-4 py-2 rounded-lg transition-colors',
            activeTab === tab.id ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
          )"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Settings Content -->
      <div class="flex-1 max-w-2xl">
        <!-- Profile Settings -->
        <Card v-if="activeTab === 'profile'">
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="grid gap-2">
              <label class="text-sm font-medium">Full Name</label>
              <Input value="Daksh G." />
            </div>
            <div class="grid gap-2">
              <label class="text-sm font-medium">Email</label>
              <Input value="user@example.com" disabled />
            </div>
            <div class="grid gap-2">
              <label class="text-sm font-medium">Phone Number</label>
              <Input value="+91 98765 43210" />
            </div>
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        <!-- Security Settings -->
        <Card v-if="activeTab === 'security'">
          <CardHeader>
            <CardTitle>Security</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="grid gap-2">
              <label class="text-sm font-medium">Current Password</label>
              <Input type="password" />
            </div>
            <div class="grid gap-2">
              <label class="text-sm font-medium">New Password</label>
              <Input type="password" />
            </div>
            <div class="grid gap-2">
              <label class="text-sm font-medium">Confirm New Password</label>
              <Input type="password" />
            </div>
            <Button>Update Password</Button>
          </CardContent>
        </Card>

        <!-- Preferences -->
        <Card v-if="activeTab === 'preferences'">
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="flex items-center justify-between">
              <div class="space-y-0.5">
                <div class="font-medium">Email Notifications</div>
                <div class="text-sm text-muted-foreground">Receive updates about your tax filing</div>
              </div>
              <input type="checkbox" checked class="h-4 w-4" />
            </div>
            <div class="flex items-center justify-between">
              <div class="space-y-0.5">
                <div class="font-medium">Dark Mode</div>
                <div class="text-sm text-muted-foreground">Toggle dark theme</div>
              </div>
              <input type="checkbox" class="h-4 w-4" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { cn } from '@/lib/utils'
import BackButton from '@/components-vue/navigation/BackButton.vue'
import Card from '@/components-vue/ui/Card.vue'
import CardHeader from '@/components-vue/ui/CardHeader.vue'
import CardTitle from '@/components-vue/ui/CardTitle.vue'
import CardContent from '@/components-vue/ui/CardContent.vue'
import Input from '@/components-vue/ui/Input.vue'
import Button from '@/components-vue/ui/Button.vue'

const activeTab = ref('profile')

const tabs = [
  { id: 'profile', label: 'Profile' },
  { id: 'security', label: 'Security' },
  { id: 'preferences', label: 'Preferences' },
]
</script>
