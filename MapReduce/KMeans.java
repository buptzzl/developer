package kmeans;
// 特点：  循环聚类的实现策略。  
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Vector;
 
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.filecache.DistributedCache;
// DistributedCache，它主要用于Mapper和Reducer之间共享数据, 属性：只读。
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;
 
public class KMeans extends Configured implements Tool{
    private static final Log log = LogFactory.getLog(KMeans2.class);
 
    private static final int K = 10;
    private static final int MAXITERATIONS = 300;
    private static final double THRESHOLD = 0.01;
     
    public static boolean stopIteration(Configuration conf) throws IOException{
        FileSystem fs=FileSystem.get(conf);
        Path pervCenterFile=new Path("/user/orisun/input/centers");
        Path currentCenterFile=new Path("/user/orisun/output/part-r-00000");
        if(!(fs.exists(pervCenterFile) && fs.exists(currentCenterFile))){
            log.info("两个质心文件需要同时存在");
            System.exit(1);
        }
        //比较前后两次质心的变化是否小于阈值，决定迭代是否继续
        boolean stop=true;
        String line1,line2;
        FSDataInputStream in1=fs.open(pervCenterFile);
        FSDataInputStream in2=fs.open(currentCenterFile);
        InputStreamReader isr1=new InputStreamReader(in1);
        InputStreamReader isr2=new InputStreamReader(in2);
        BufferedReader br1=new BufferedReader(isr1);
        BufferedReader br2=new BufferedReader(isr2);
        Sample prevCenter,currCenter;
        while((line1=br1.readLine())!=null && (line2=br2.readLine())!=null){
            prevCenter=new Sample();
            currCenter=new Sample();
            String []str1=line1.split("\\s+");
            String []str2=line2.split("\\s+");
            assert(str1[0].equals(str2[0]));
            for(int i=1;i<=Sample.DIMENTION;i++){
                prevCenter.arr[i-1]=Double.parseDouble(str1[i]);
                currCenter.arr[i-1]=Double.parseDouble(str2[i]);
            }
            if(Sample.getEulerDist(prevCenter, currCenter)>THRESHOLD){
                stop=false;
                break;
            }
        }
        //如果还要进行下一次迭代，就用当前质心替代上一次的质心
        if(stop==false){
            fs.delete(pervCenterFile,true);
            if(fs.rename(currentCenterFile, pervCenterFile)==false){
                log.error("质心文件替换失败");
                System.exit(1);
            }
        }
        return stop;
    }
     
    public static class ClusterMapper extends Mapper<LongWritable, Text, IntWritable, Sample> {
        Vector<Sample> centers = new Vector<Sample>();
        @Override
        //清空centers
        public void setup(Context context){
            for (int i = 0; i < K; i++) {
                centers.add(new Sample());
            }
        }
        @Override
        //从输入文件读入centers
        public void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
        // TODO : 可以优化为直接进行聚类，写结果文件并更新类中心。无需Reduce 部分。
            String []str=value.toString().split("\\s+");
            if(str.length!=Sample.DIMENTION+1){
                log.error("读入centers时维度不对");
                System.exit(1);
            }
            int index=Integer.parseInt(str[0]);
            for(int i=1;i<str.length;i++)
                centers.get(index).arr[i-1]=Double.parseDouble(str[i]);
        }
        @Override
        //找到每个数据点离哪个质心最近
        public void cleanup(Context context) throws IOException,InterruptedException {
            Path []caches=DistributedCache.getLocalCacheFiles(context.getConfiguration());
            if(caches==null || caches.length<=0){
                log.error("data文件不存在");
                System.exit(1);
            }
            BufferedReader br=new BufferedReader(new FileReader(caches[0].toString()));
            Sample sample;
            String line;
            while((line=br.readLine())!=null){
                sample=new Sample();
                String []str=line.split("\\s+");
                for(int i=0;i<Sample.DIMENTION;i++)
                    sample.arr[i]=Double.parseDouble(str[i]);
                 
                int index=-1;
                double minDist=Double.MAX_VALUE;
                for(int i=0;i<K;i++){
                    double dist=Sample.getEulerDist(sample, centers.get(i));
                    if(dist<minDist){
                        minDist=dist;
                        index=i;
                    }
                }
                context.write(new IntWritable(index), sample); // 类ID-Data.Sample 需保持
            }
        }
    }
     
    public static class UpdateCenterReducer extends Reducer<IntWritable, Sample, IntWritable, Sample> {
        int prev=-1;
        Sample center=new Sample();;
        int count=0;
        @Override
        //更新每个质心（除最后一个）
        public void reduce(IntWritable key,Iterable<Sample> values,Context context) throws IOException,InterruptedException{
            while(values.iterator().hasNext()){
                Sample value=values.iterator().next();
                if(key.get()!=prev){
                    if(prev!=-1){
                        for(int i=0;i<center.arr.length;i++)
                            center.arr[i]/=count;       
                        context.write(new IntWritable(prev), center);
                    }
                    center.clear();
                    prev=key.get();
                    count=0;
                }
                for(int i=0;i<Sample.DIMENTION;i++)
                    center.arr[i]+=value.arr[i];
                count++;
            }
        }
        @Override
        //更新最后一个质心
        public void cleanup(Context context) throws IOException,InterruptedException{
            for(int i=0;i<center.arr.length;i++)
                center.arr[i]/=count;
            context.write(new IntWritable(prev), center);
        }
    }
 
    @Override
    public int run(String[] args) throws Exception {
        Configuration conf=getConf();
        FileSystem fs=FileSystem.get(conf);
        Job job=new Job(conf);
        job.setJarByClass(KMeans.class);
         
        //质心文件每行的第一个数字是索引
        FileInputFormat.setInputPaths(job, "/user/orisun/input/centers");
        Path outDir=new Path("/user/orisun/output");
        fs.delete(outDir,true);
        FileOutputFormat.setOutputPath(job, outDir);
         
        job.setInputFormatClass(TextInputFormat.class);
        job.setOutputFormatClass(TextOutputFormat.class);
        job.setMapperClass(ClusterMapper.class);
        job.setReducerClass(UpdateCenterReducer.class);
        job.setOutputKeyClass(IntWritable.class);
        job.setOutputValueClass(Sample.class);
         
        return job.waitForCompletion(true)?0:1;
    }
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        FileSystem fs=FileSystem.get(conf);
         
        //样本数据文件中每个样本不需要标记索引
        Path dataFile=new Path("/user/orisun/input/data");
        DistributedCache.addCacheFile(dataFile.toUri(), conf);
 
        int iteration = 0;
        int success = 1;
        do {
            success ^= ToolRunner.run(conf, new KMeans(), args);
            log.info("iteration "+iteration+" end");
        } while (success == 1 && iteration++ < MAXITERATIONS
                && (!stopIteration(conf)));
        log.info("Success.Iteration=" + iteration);
         
        //迭代完成后再执行一次mapper，输出每个样本点所属的分类--在/user/orisun/output2/part-m-00000中
        //质心文件保存在/user/orisun/input/centers中
        // TODO : 可以优化为使用 ToolRunner 中的KMeans 实例，调用run()即可。
        Job job=new Job(conf);
        job.setJarByClass(KMeans.class);
         
        FileInputFormat.setInputPaths(job, "/user/orisun/input/centers");
        Path outDir=new Path("/user/orisun/output2");
        fs.delete(outDir,true);
        FileOutputFormat.setOutputPath(job, outDir);
         
        job.setInputFormatClass(TextInputFormat.class);
        job.setOutputFormatClass(TextOutputFormat.class);
        job.setMapperClass(ClusterMapper.class);
        job.setNumReduceTasks(0);
        job.setOutputKeyClass(IntWritable.class);
        job.setOutputValueClass(Sample.class);
         
        job.waitForCompletion(true);
    }
}