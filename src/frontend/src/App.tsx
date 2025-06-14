import { Container, Title, Text, Stack } from '@mantine/core'

function App() {
  return (
    <Container size="sm" py="xl">
      <Stack align="center" gap="lg">
        <Title order={1} ta="center">
          AI Community
        </Title>
        <Text size="lg" ta="center" c="dimmed">
          モダンでカジュアルなリアルタイムチャットアプリケーション
        </Text>
        <Text ta="center">
          現在、ステップ1（初期セットアップ）が完了しました。
          <br />
          次のステップでチャットアプリの機能を実装していきます。
        </Text>
      </Stack>
    </Container>
  )
}

export default App
