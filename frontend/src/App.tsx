import React, { useState, useEffect } from 'react';

// レコードの型定義
type RecordType = {
  date: string;
  category: string;
  amount: number;
};

function App() {
  const [records, setRecords] = useState<RecordType[]>([]);
  const [date, setDate] = useState('');
  const [category, setCategory] = useState('');
  const [amount, setAmount] = useState<number>(0);

  // 初回読み込みで一覧を取ってくる
  useEffect(() => {
    fetch("http://localhost:8000/records")
      .then((res) => res.json())
      .then((data: RecordType[]) => {
        setRecords(data);
      })
      .catch((err) => console.error(err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newRecord = {
      date,
      category,
      amount,
    };

    await fetch("http://localhost:8000/records", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newRecord),
    });

    // 送信後、一覧を更新
    fetch("http://localhost:8000/records")
      .then((res) => res.json())
      .then((data: RecordType[]) => {
        setRecords(data);
      });
  };

  return (
    <>
      <div>
        <h1>家計簿テストページ</h1>
        <form onSubmit={handleSubmit}>
          <div>
            <label>日付：</label>
            <input id="date" type="date" value={date} onChange={(e) => setDate(e.target.value)}
            />
          </div>

          <div>
            <label>カテゴリ：</label>
            <input id="category" type="text" value={category} onChange={(e) => setCategory(e.target.value)}
            />
          </div>

          <div>
            <label>金額：</label>
            <input id="amount" type="text" value={amount} onChange={(e) => setAmount(parseInt(e.target.value, 10))}
            />
          </div>

          <button type="submit">送信</button>
        </form>

        <h2>記録一覧</h2>
        <ul>
          {records.map((r, idx) => (
            <li key={idx}>
              {r.date} - {r.category} - ¥{r.amount}
            </li>
          ))}
        </ul>
      </div>
    </>
  )
}

export default App;