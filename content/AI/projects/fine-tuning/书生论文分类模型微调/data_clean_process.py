import json
import argparse
import os

def extract_category_mapping():
    """定义类别到选项的映射"""
    category_to_option = {
        'quant-ph': 'A',
        'physics.chem-ph': 'B', 
        'physics.atom-ph': 'C',
        'cond-mat.soft': 'D',
        'cs.RO': 'E',
        'cs.CL': 'F',
        'cs.SE': 'G',
        'cs.IR': 'H',
        'hep-th': 'I',
        'hep-ph': 'J',
        'physics.optics': 'K',
        'cs.AI': 'L',
        'cs.CV': 'M',
        'nucl-th': 'N',
        'astro-ph': 'O',
        'math.PR': 'P',
        'cs.OS': 'Q',
        'eess.SP': 'R',
        'math.OC': 'S',
        'math.DS': 'T',
        'math.DG': 'U',
        'math.MP': 'V',
        'cs.MM': 'W',
        'stat.ME': 'X',
        'math.CO': 'Y',
        'cs.NE': 'Z'
    }
    return category_to_option

def get_category_options_text():
    """生成选项文本"""
    options = [
        "A. quant-ph", "B. physics.chem-ph", "C. physics.atom-ph", "D. cond-mat.soft",
        "E. cs.RO", "F. cs.CL", "G. cs.SE", "H. cs.IR", "I. hep-th", "J. hep-ph",
        "K. physics.optics", "L. cs.AI", "M. cs.CV", "N. nucl-th", "O. astro-ph",
        "P. math.PR", "Q. cs.OS", "R. eess.SP", "S. math.OC", "T. math.DS",
        "U. math.DG", "V. math.MP", "W. cs.MM", "X. stat.ME", "Y. math.CO", "Z. cs.NE"
    ]
    return "\n".join(options)

def process_paper(paper_data, verbose=False):
    """处理单篇论文数据"""
    category_mapping = extract_category_mapping()
    
    # 提取基本信息
    paper_id = paper_data.get('id', '')
    title = paper_data.get('title', '').replace('\n', ' ').strip()
    authors = paper_data.get('authors', '')
    abstract = paper_data.get('abstract', '').replace('\n', ' ').strip()
    categories = paper_data.get('categories', '')
    
    # 检查是否包含多个类别（用空格分隔）
    category_list = categories.split()
    if len(category_list) > 1:
        if verbose:
            print(f"跳过多类别论文 {paper_id}: {categories}")
        return None
    
    # 检查类别是否在我们的目标列表中
    target_category = category_list[0] if category_list else ''
    if target_category not in category_mapping:
        if verbose:
            print(f"跳过非目标类别论文 {paper_id}: {target_category}")
        return None
    
    # 获取对应的选项字母
    correct_option = category_mapping[target_category]
    
    # 构建human问题
    options_text = get_category_options_text()
    human_content = f"Based on the title '{title}', authors '{authors}', and abstract '{abstract}', please determine the scientific category of this paper.\n\n{options_text}"
    
    # 构建JSONL条目
    jsonl_entry = {
        "system": "你是个优秀的论文分类师",
        "conversation": [
            {
                "human": human_content,
                "assistant": correct_option
            }
        ]
    }
    
    if verbose:
        print(f"处理论文 {paper_id}: {target_category} -> {correct_option}")
    
    return jsonl_entry

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='将arXiv论文JSON数据转换为分类训练JSONL格式')
    
    parser.add_argument('input_file', 
                        help='输入的JSON文件路径')
    parser.add_argument('output_file', 
                        help='输出的JSONL文件路径')
    parser.add_argument('--verbose', '-v', 
                        action='store_true',
                        help='显示详细处理信息')
    parser.add_argument('--force', '-f',
                        action='store_true', 
                        help='强制覆盖输出文件')
    parser.add_argument('--limit', '-l',
                        type=int,
                        help='限制处理的论文数量')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 {args.input_file} 不存在")
        return 1
    
    # 检查输出文件是否已存在
    if os.path.exists(args.output_file) and not args.force:
        response = input(f"输出文件 {args.output_file} 已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("操作取消")
            return 1
    
    try:
        # 读取JSON数据
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # 按行分割处理每个JSON对象
        lines = content.split('\n')
        
        processed_count = 0
        skipped_count = 0
        total_lines = len([line for line in lines if line.strip()])
        
        print(f"开始处理 {total_lines} 行数据...")
        
        with open(args.output_file, 'w', encoding='utf-8') as f:
            for i, line in enumerate(lines):
                if line.strip():
                    # 检查是否达到限制数量
                    if args.limit and processed_count >= args.limit:
                        print(f"达到处理限制 {args.limit}，停止处理")
                        break
                    
                    try:
                        paper_data = json.loads(line)
                        result = process_paper(paper_data, args.verbose)
                        
                        if result:
                            f.write(json.dumps(result, ensure_ascii=False) + '\n')
                            processed_count += 1
                        else:
                            skipped_count += 1
                        
                        # 显示进度
                        if not args.verbose and (i + 1) % 100 == 0:
                            print(f"已处理 {i + 1}/{total_lines} 行，成功: {processed_count}，跳过: {skipped_count}")
                            
                    except json.JSONDecodeError as e:
                        if args.verbose:
                            print(f"第 {i+1} 行JSON解析错误: {e}")
                        skipped_count += 1
        
        print(f"\n处理完成!")
        print(f"成功处理: {processed_count} 篇论文")
        print(f"跳过: {skipped_count} 篇论文")
        print(f"输出文件: {args.output_file}")
        
        return 0
        
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 {args.input_file}")
        return 1
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        return 1

if __name__ == "__main__":
    exit(main())