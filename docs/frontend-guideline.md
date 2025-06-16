# Frontend固有のルール

1. **フレームワーク・ライブラリ**
   - パッケージ管理: npm（frontendディレクトリ内）
   - インストール: `npm install package`
   - 起動: `npm run dev`

2. **コンポーネント設計**
   - 関数コンポーネント + TypeScript
   - props型定義は必須
   - Mantineコンポーネントを優先使用

3. **状態管理**
   - 初期段階はReact useState
   - 将来的にContext API追加予定

4. **スタイリング**
   - Mantineテーマシステム使用
   - グローバルCSS最小限
   - CSS-in-JSアプローチ
