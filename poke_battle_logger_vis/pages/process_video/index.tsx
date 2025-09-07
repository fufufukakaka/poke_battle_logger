import React, { useState } from "react";
import axios from 'axios';
import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import { ServerHost } from "../../util"
import useSWR from "swr";
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Loader2 } from 'lucide-react';

interface videoFormat {
    isValid: boolean;
    is1080p: boolean;
    is30fps: boolean;
}

interface videoStatus {
  videoId: string;
  registeredAt: string;
  status: string;
}

const fetcher = async (url: string) => {
  const res = await fetch(url);
  const data = await res.json();
  return data
}

const ProcessVideoPage = () => {
  const [videoId, setVideoId] = useState("");
  const [videoFormat, setVideoFormat] = useState<videoFormat | undefined>(undefined);
  const [langInVideo, setLangInVideo] = useState('en')
  const [videoStatusLogDetail, setVideoStatusLogDetail] = useState<string[]>([])
  const [isShowFinalResult, setIsShowFinalResult] = useState<boolean>(false)
  const [finalResult, setFinalResult] = useState<number | undefined>(undefined)

  const { user } = useAuth0();
  const trainerId = user?.sub?.replace("|", "_");
  const { data: dataVideoStatus } = useSWR(`/api/get_video_process_status?trainerId=${trainerId}`, fetcher);

  const handleOnChange = (value: string) => {
    setVideoId(value);
  };

  const handleOnClick = async () => {
    const checkResult: {"data": videoFormat} = await axios.get(`${ServerHost}/api/v1/check_video_format?videoId=${videoId}`);
    setVideoFormat(checkResult.data)
  };

  const handleExtractJob = async () => {
    const requestUrl = finalResult ? `${ServerHost}/api/v1/extract_stats_from_video?videoId=${videoId}&language=${langInVideo}&trainerId=${user?.sub?.replace("|", "_")}&finalResult=${finalResult}` : `${ServerHost}/api/v1/extract_stats_from_video?videoId=${videoId}&language=${langInVideo}&trainerId=${user?.sub?.replace("|", "_")}`
    await axios.get(requestUrl);
    dataVideoStatus.push({
      videoId: videoId,
      registeredAt: new Date().toLocaleString(),
      status: "Processing..."
    })
  }

  const processLogDetailFetchHandler = async (targetVideoId: string) => {
    const res = await axios.get(`/api/get_battle_video_detail_status_log?videoId=${targetVideoId}`);
    setVideoStatusLogDetail(res.data);
  }

  const showFinalResultInput = () => {
    setIsShowFinalResult(!isShowFinalResult)
  }

  const handleFinalResultChange = (value: string) => {
    setFinalResult(parseInt(value))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8">
        <div className="flex items-center gap-0">
          <h1 className="text-3xl font-bold p-1">対戦データ登録</h1>
          <img src="./n426.gif" alt="フワライド" className="w-12 h-12" />
        </div>
        <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
            <div className="flex flex-col items-start space-y-4">
            <p>Youtube の動画(1080p: 30fps) のID を入力してください</p>
            <div className="flex w-full max-w-sm">
                <span className="inline-flex items-center px-3 text-sm text-muted-foreground bg-muted border border-r-0 border-input rounded-l-md">
                  https://www.youtube.com/watch?v=
                </span>
                <Input 
                  placeholder='videoId' 
                  value={videoId} 
                  onChange={(e) => handleOnChange(e.target.value)}
                  className="rounded-l-none"
                />
            </div>
            <Button onClick={() => handleOnClick()}>Check Format</Button>
            </div>
        </div>
        <Separator className="my-4" />
        <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
            {videoFormat && (
                <p>動画のフォーマット: {videoFormat.isValid ? <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100">OK</Badge> : <Badge variant="destructive">NO</Badge>} </p>
            )}
            {videoFormat && !videoFormat.isValid && (
                <p>動画が 1080p かどうか: {videoFormat.is1080p ? <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100">OK</Badge> : <Badge variant="destructive">NO</Badge>}</p>
            )}
            {videoFormat && !videoFormat.isValid && (
                <p>動画が 30fps かどうか: {videoFormat.is30fps ? <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100">OK</Badge> : <Badge variant="destructive">NO</Badge>}</p>
            )}
        </div>
        {videoFormat && videoFormat.isValid ? (
          <>
          <Separator className="my-4" />
            <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
              <div className="mb-4">
                <RadioGroup value={langInVideo} onValueChange={setLangInVideo}>
                  <div className="flex items-center space-x-6">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="en" id="en" />
                      <Label htmlFor="en">English</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="ja" id="ja" />
                      <Label htmlFor="ja">Japanese</Label>
                    </div>
                  </div>
                </RadioGroup>
              </div>
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">
                    最後の対戦終了後の順位が動画に記録されていない場合、こちらに入力してください
                  </Label>
                  <div className="mt-2">
                    <Switch checked={isShowFinalResult} onCheckedChange={showFinalResultInput} />
                  </div>
                  {isShowFinalResult && (
                    <div className="mt-2 max-w-xs">
                      <Input 
                        type="number"
                        value={finalResult || ''} 
                        onChange={(e) => handleFinalResultChange(e.target.value)}
                        placeholder="順位を入力"
                      />
                    </div>
                  )}
                </div>
              </div>
              <Button 
                className="bg-green-600 hover:bg-green-700 mt-4" 
                onClick={() => handleExtractJob()}
              >
                Start Process Video
              </Button>
            </div>
          </>
        ) : null}
        {dataVideoStatus && dataVideoStatus.length > 0 ? (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>動画ID</TableHead>
                  <TableHead>登録日</TableHead>
                  <TableHead>処理状況</TableHead>
                  <TableHead>処理状況詳細</TableHead>
                  <TableHead>動画を開く</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dataVideoStatus.map((videoStatus: videoStatus, index: number) => {
                  return (
                    <TableRow key={index}>
                      <TableCell>{videoStatus.videoId}</TableCell>
                      <TableCell>{videoStatus.registeredAt}</TableCell>
                      <TableCell><Badge variant="secondary">{videoStatus.status}</Badge></TableCell>
                      <TableCell>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button 
                              variant="outline" 
                              onClick={() => processLogDetailFetchHandler(videoStatus.videoId)}
                            >
                              処理詳細
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-80">
                            <div className="space-y-2">
                              <h4 className="font-medium">処理ログ</h4>
                              <ol className="list-decimal list-inside space-y-1">
                                {videoStatusLogDetail.length > 0 
                                  ? videoStatusLogDetail.map((log, index) => (
                                      <li key={index} className="text-sm">{log}</li>
                                    ))
                                  : <div className="flex items-center space-x-2">
                                      <Loader2 className="h-4 w-4 animate-spin" />
                                      <span className="text-sm">読み込み中...</span>
                                    </div>
                                }
                              </ol>
                            </div>
                          </PopoverContent>
                        </Popover>
                      </TableCell>
                      <TableCell>
                        <Button 
                          variant="outline" 
                          onClick={() => window.open(`https://www.youtube.com/watch?v=${videoStatus.videoId}`)}
                        >
                          Open Video
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        ) : (
          <p>まだ登録された動画がありません。動画を登録して対戦情報を抽出してみましょう。</p>
        )}
      </div>
    </div>
  );
};

// このページは認証が必要なため、SSGではなくSSRを使用
export async function getServerSideProps() {
  // 認証が必要なページなので、常に動的レンダリング
  return {
    props: {}
  };
}

export default withAuthenticationRequired(ProcessVideoPage);
