#!/usr/bin/env python3
"""
电商全链路多Agent智能体系统 - 命令行入口
"""

import sys
import argparse
import json
from config.settings import get_settings
from core.coordinator import EcommerceAgentCoordinator
from utils.llm_factory import LLMFactory

def main():
    parser = argparse.ArgumentParser(
        description="电商全链路多Agent智能体系统"
    )
    
    parser.add_argument(
        "--platform", "-p",
        type=str,
        default="抖音",
        choices=["抖音", "淘宝", "拼多多", "小红书"],
        help="目标电商平台 (默认: 抖音)"
    )
    
    parser.add_argument(
        "--llm", "-l",
        type=str,
        default="mock",
        choices=["mock", "openai", "anthropic"],
        help="LLM提供商 (默认: mock)"
    )
    
    parser.add_argument(
        "--agent", "-a",
        type=str,
        default=None,
        choices=["market", "product", "content", "ad", "after_sales"],
        help="只运行特定Agent (默认: 运行全部)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="结果输出到JSON文件"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    settings = get_settings()
    
    print("=" * 60)
    print("🛒 电商全链路多Agent智能体系统")
    print("=" * 60)
    print(f"平台: {args.platform}")
    print(f"LLM: {args.llm}")
    print("-" * 60)
    
    # 创建LLM
    llm = None
    if args.llm != "mock":
        try:
            print(f"正在加载{args.llm}模型...")
            llm = LLMFactory.create_llm(provider=args.llm)
            print("✅ LLM加载成功")
        except Exception as e:
            print(f"❌ LLM加载失败: {str(e)}")
            print("将使用模拟模式运行")
            args.llm = "mock"
    
    # 创建协调器
    coordinator = EcommerceAgentCoordinator(llm=llm)
    
    # 运行
    try:
        if args.agent:
            # 只运行特定Agent
            print(f"▶️  正在运行Agent: {args.agent}")
            
            # 根据Agent类型准备参数
            kwargs = {}
            if args.agent == "market":
                kwargs["platform"] = args.platform
            elif args.agent == "product":
                # 需要先运行市场洞察
                print("  先运行市场洞察...")
                market_result = coordinator.run_single_agent("market", platform=args.platform)
                kwargs["market_insight"] = market_result
            elif args.agent == "content":
                # 需要先运行市场洞察和选品
                print("  先运行市场洞察和选品...")
                market_result = coordinator.run_single_agent("market", platform=args.platform)
                product_result = coordinator.run_single_agent("product", market_insight=market_result)
                kwargs["selected_products"] = product_result["selected_products"]
            elif args.agent == "ad":
                # 需要前面的步骤
                print("  先运行前置Agent...")
                market_result = coordinator.run_single_agent("market", platform=args.platform)
                product_result = coordinator.run_single_agent("product", market_insight=market_result)
                content_result = coordinator.run_single_agent("content", selected_products=product_result["selected_products"])
                kwargs["content_matrix"] = content_result["content_matrix"]
            elif args.agent == "after_sales":
                # 需要前面的步骤
                print("  先运行前置Agent...")
                market_result = coordinator.run_single_agent("market", platform=args.platform)
                product_result = coordinator.run_single_agent("product", market_insight=market_result)
                content_result = coordinator.run_single_agent("content", selected_products=product_result["selected_products"])
                ad_result = coordinator.run_single_agent("ad", content_matrix=content_result["content_matrix"])
                kwargs["ad_optimization"] = ad_result
            
            result = coordinator.run_single_agent(args.agent, **kwargs)
            print(f"✅ Agent {args.agent} 执行完成")
            
        else:
            # 运行完整工作流
            print("▶️  启动完整工作流...")
            result = coordinator.run_full_workflow(platform=args.platform)
            print("✅ 完整工作流执行完成")
        
        # 输出结果摘要
        print("\n" + "=" * 60)
        print("📊 结果摘要")
        print("=" * 60)
        
        if args.agent:
            # 单个Agent结果
            print(f"Agent: {args.agent}")
            if args.verbose:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 完整结果
            print(f"平台: {result['platform']}")
            print(f"执行时间: {result['execution_info']['execution_time_seconds']}秒")
            
            kpis = result['summary_kpis']
            print("\n预期提升:")
            perf = kpis['performance_improvement']
            print(f"  • ROI提升: {perf['estimated_roi_improvement']}")
            print(f"  • 成本降低: {perf['estimated_cost_reduction']}")
            print(f"  • 效率提升: {perf['estimated_efficiency_improvement']}")
            
            print("\n执行摘要:")
            print(result['executive_summary'])
        
        # 保存到文件
        if args.output:
            print(f"\n💾 保存结果到: {args.output}")
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print("✅ 保存完成")
        
        print("\n" + "=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行出错: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
