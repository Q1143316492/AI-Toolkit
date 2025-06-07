#!/usr/bin/env python311
# -*- coding: utf-8 -*-
"""
Copilot Chat JSON to Markdown Converter
Converts exported Copilot chat JSON to readable Markdown format

Features:
- Parses GitHub Copilot Chat exported JSON files
- Converts to well-formatted Markdown with proper structure
- Identifies specific tool calls (run_in_terminal, create_file, etc.)
- Shows tool parameters and outputs in readable format
- Handles file references and variable data
- Supports command line arguments for input/output files

Usage:
    python ChatToMD.py                          # Uses chat.json -> chat_conversation.md
    python ChatToMD.py input.json               # Uses input.json -> input.md
    python ChatToMD.py input.json output.md     # Specify both input and output

Author: AI-Toolkit
Version: 2.0
"""

import json
import datetime
import re
from typing import Dict, List, Any, Optional

# Constants
MARKDOWN_FILE_EXT = ".md"
JSON_FILE_EXT = ".json"

def LoadJsonFile(szFilePath: str) -> Optional[Dict[str, Any]]:
    """Load JSON file and return parsed data"""
    try:
        with open(szFilePath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found - {szFilePath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return None
    except Exception as e:
        print(f"Error: Failed to load file - {e}")
        return None

def FormatTimestamp(nTimestamp: int) -> str:
    """Convert timestamp to readable format"""
    try:
        dtTime = datetime.datetime.fromtimestamp(nTimestamp / 1000)
        return dtTime.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown Time"

def ExtractFileName(szFilePath: str) -> str:
    """Extract filename from file path"""
    if not szFilePath:
        return "Unknown File"
    return szFilePath.split('\\')[-1].split('/')[-1]

def ProcessResponsePart(dictPart: Dict[str, Any]) -> str:
    """Process a single response part and return formatted text"""
    szResult = ""
    
    if dictPart.get("kind") == "inlineReference":
        dictRef = dictPart.get("inlineReference", {})
        szName = dictRef.get("name", "Unknown Reference")
        szResult += f"[{szName}]"
    elif dictPart.get("kind") == "codeblockUri":
        dictUri = dictPart.get("uri", {})
        szPath = dictUri.get("fsPath", "")
        szFileName = ExtractFileName(szPath)
        szResult += f"\n\n**File:** `{szFileName}`\n"
    elif dictPart.get("kind") == "toolInvocationSerialized":
        szResult += _ProcessToolInvocation(dictPart)
    elif dictPart.get("value"):
        szValue = dictPart.get("value", "")
        # Handle nested dict in value (like MCP tool calls)
        if isinstance(szValue, dict):
            szResult += _ProcessToolValue(szValue)
        else:
            # Clean up markdown formatting
            szValue = re.sub(r'````\n', '', szValue)
            szResult += szValue
    
    return szResult

def _ProcessToolInvocation(dictTool: Dict[str, Any]) -> str:
    """Process tool invocation and return formatted text"""
    szResult = ""
    
    # Extract tool name from toolSpecificData
    dictToolSpecific = dictTool.get("toolSpecificData", {})
    szToolName = _ExtractToolName(dictToolSpecific)
    
    # Get tool message
    dictInvocationMsg = dictTool.get("invocationMessage", {})
    if isinstance(dictInvocationMsg, dict):
        szMessage = dictInvocationMsg.get("value", "")
    else:
        szMessage = str(dictInvocationMsg) if dictInvocationMsg else ""
    
    # Format tool call with specific name
    if szToolName:
        szResult += f"\n**🔧 Tool Call:** {szToolName}"
        if szMessage and szMessage not in ['Using ""', '']:
            # Extract explanation from message if available
            szExplanation = _ExtractExplanation(szMessage)
            if szExplanation:
                szResult += f" - {szExplanation}"
        szResult += "\n"
    elif szMessage and szMessage != 'Using ""':
        szResult += f"\n**🔧 Tool Call:** {szMessage}\n"    
    # Get tool parameters/input
    dictRawInput = dictToolSpecific.get("rawInput", {})
    if dictRawInput:
        # Special handling for SendGmCommandToGame: show formatted GM script directly
        if "szGmScript" in dictRawInput:
            szGmScript = dictRawInput["szGmScript"]
            if isinstance(szGmScript, str) and ("\\n" in szGmScript or "\n" in szGmScript):
                szResult += "**GM Script:**\n```python\n"
                szFormattedScript = szGmScript.replace('\\n', '\n')
                # Remove leading ! if present
                if szFormattedScript.startswith('!'):
                    szFormattedScript = szFormattedScript[1:]
                szResult += szFormattedScript
                szResult += "\n```\n"
            else:
                # Single line GM script, show as parameters
                szResult += "**Parameters:**\n```json\n"
                szResult += json.dumps(dictRawInput, indent=2, ensure_ascii=False)
                szResult += "\n```\n"
        # Special formatting for common tools
        elif szToolName == "run_in_terminal":
            szCommand = dictRawInput.get("command", "")
            szExplanation = dictRawInput.get("explanation", "")
            if szCommand:
                if szExplanation:
                    szResult += f"**Command:** {szExplanation}\n```bash\n{szCommand}\n```\n"
                else:
                    szResult += f"**Command:**\n```bash\n{szCommand}\n```\n"
        elif szToolName in ["replace_string_in_file", "insert_edit_into_file", "create_file"]:
            szFilePath = dictRawInput.get("filePath", "")
            if szFilePath:
                szFileName = ExtractFileName(szFilePath)
                szResult += f"\n**File:** `{szFileName}`\n"
            if szToolName != "create_file":
                szResult += "\n```\n"
                if "oldString" in dictRawInput:
                    szOldString = dictRawInput["oldString"][:200] + "..." if len(dictRawInput["oldString"]) > 200 else dictRawInput["oldString"]
                    szResult += f"# Replacing:\n{szOldString}\n\n"
                if "code" in dictRawInput or "newString" in dictRawInput:
                    szNewCode = dictRawInput.get("code", dictRawInput.get("newString", ""))
                    szNewCode = szNewCode[:500] + "..." if len(szNewCode) > 500 else szNewCode
                    szResult += f"# With:\n{szNewCode}\n"
                szResult += "```\n"
        else:
            # Regular tool parameters - show only important ones
            dictDisplayInput = {}
            for szKey, szValue in dictRawInput.items():
                if szKey in ["query", "symbolName", "url", "explanation", "reason"]:
                    dictDisplayInput[szKey] = szValue
                elif isinstance(szValue, str) and len(szValue) < 100:
                    dictDisplayInput[szKey] = szValue.replace('\\n', '\n')
            
            if dictDisplayInput:
                szResult += "**Parameters:**\n```json\n"
                szResult += json.dumps(dictDisplayInput, indent=2, ensure_ascii=False)
                szResult += "\n```\n"    # Get tool result/output
    dictResultDetails = dictTool.get("resultDetails", {})
    if dictResultDetails:
        listOutput = dictResultDetails.get("output", [])
        bIsError = dictResultDetails.get("isError", False)
        
        if listOutput:
            if bIsError:
                szResult += "**⚠️ Error:**\n"
            else:
                # For successful commands, show abbreviated output
                if szToolName == "run_in_terminal":
                    szResult += "**Output:**\n"
                elif szToolName in ["create_file", "replace_string_in_file", "insert_edit_into_file"]:
                    # For file operations, just show success/failure
                    szResult += "**Result:** File operation completed\n"
                    return szResult
                else:
                    szResult += "**Output:**\n"
            
            for dictOutputItem in listOutput:
                if isinstance(dictOutputItem, dict):
                    szOutputValue = dictOutputItem.get("value", "")
                    if szOutputValue:
                        # Convert escaped newlines to real newlines
                        szOutputValue = szOutputValue.replace('\\n', '\n')
                        # Truncate very long output
                        if len(szOutputValue) > 1000:
                            szOutputValue = szOutputValue[:1000] + "\n... (output truncated)"
                        szResult += f"```\n{szOutputValue}\n```\n"
                else:
                    szOutputStr = str(dictOutputItem)
                    # Convert escaped newlines to real newlines
                    szOutputStr = szOutputStr.replace('\\n', '\n')
                    # Truncate very long output
                    if len(szOutputStr) > 1000:
                        szOutputStr = szOutputStr[:1000] + "\n... (output truncated)"
                    szResult += f"```\n{szOutputStr}\n```\n"
    
    return szResult

def _ProcessToolValue(dictValue: Dict[str, Any]) -> str:
    """Process tool value dict and return formatted text"""
    szValue = dictValue.get("value", "")
    if szValue:
        return f"*{szValue}*"
    return ""

def ProcessVariables(listVariables: List[Dict[str, Any]]) -> str:
    """Process variable data and return formatted text"""
    if not listVariables:
        return ""
    
    szResult = "**Referenced Files:**\n"
    for dictVar in listVariables:
        if dictVar.get("kind") == "file":
            szName = dictVar.get("name", "Unknown File")
            dictValue = dictVar.get("value", {})
            szPath = dictValue.get("fsPath", "")
            if szPath:
                szResult += f"- `{szName}` - {szPath}\n"
    
    szResult += "\n"
    return szResult

def ConvertChatToMarkdown(dictChatData: Dict[str, Any]) -> str:
    """Convert chat JSON data to Markdown format"""
    szMarkdown = ""
    
    # Header
    szRequester = dictChatData.get("requesterUsername", "Unknown User")
    szResponder = dictChatData.get("responderUsername", "GitHub Copilot")
    
    szMarkdown += f"# Chat Conversation\n\n"
    szMarkdown += f"**Participants:** {szRequester} ↔ {szResponder}\n\n"
    
    # Process requests
    listRequests = dictChatData.get("requests", [])
    for nIndex, dictRequest in enumerate(listRequests, 1):
        # User message
        dictMessage = dictRequest.get("message", {})
        szUserText = dictMessage.get("text", "")
        if szUserText:
            szMarkdown += f"**{nIndex}.** {szUserText}\n\n"
        
        # Variables/Referenced files
        dictVariableData = dictRequest.get("variableData", {})
        listVariables = dictVariableData.get("variables", [])
        szVariableText = ProcessVariables(listVariables)
        if szVariableText:
            szMarkdown += szVariableText
        
        # Response
        listResponse = dictRequest.get("response", [])
        if listResponse:
            szResponseText = ""
            
            for dictPart in listResponse:
                szPartText = ProcessResponsePart(dictPart)
                szResponseText += szPartText
            
            # Clean up response text
            szResponseText = re.sub(r'\n{3,}', '\n\n', szResponseText)
            szResponseText = szResponseText.strip()
            
            if szResponseText:
                szMarkdown += szResponseText + "\n\n"
        
        if nIndex < len(listRequests):
            szMarkdown += "---\n\n"
    
    return szMarkdown

def _ExtractToolName(dictToolSpecific: Dict[str, Any]) -> str:
    """Extract specific tool name from tool data"""
    dictRawInput = dictToolSpecific.get("rawInput", {})
    
    # Common tool name mappings based on parameters
    if "command" in dictRawInput:
        return "run_in_terminal"
    elif "filePath" in dictRawInput and "oldString" in dictRawInput:
        return "replace_string_in_file"
    elif "filePath" in dictRawInput and "code" in dictRawInput:
        return "insert_edit_into_file"
    elif "filePath" in dictRawInput and "content" in dictRawInput:
        return "create_file"
    elif "query" in dictRawInput and not dictRawInput.get("filePaths"):
        return "semantic_search"
    elif "symbolName" in dictRawInput:
        return "list_code_usages"
    elif "filePaths" in dictRawInput and "startLineNumberBaseZero" in dictRawInput:
        return "read_file"
    elif "path" in dictRawInput:
        return "list_dir"
    elif "urls" in dictRawInput:
        return "fetch_webpage"
    elif "repo" in dictRawInput:
        return "github_repo"
    elif "projectType" in dictRawInput:
        return "get_project_setup_info"
    elif "task" in dictRawInput:
        return "create_and_run_task"
    elif "id" in dictRawInput:
        return "install_extension"
    elif "szGmScript" in dictRawInput:
        return "SendGmCommandToGame"
    
    # Try to extract from tool specific data structure
    if "tool" in dictToolSpecific:
        dictToolInfo = dictToolSpecific["tool"]
        if isinstance(dictToolInfo, dict):
            return dictToolInfo.get("name", "unknown_tool")
    
    return ""

def _ExtractExplanation(szMessage: str) -> str:
    """Extract explanation from tool message"""
    if not szMessage:
        return ""
    
    # Remove common prefixes
    szClean = szMessage.replace('Using "', '').replace('"', '')
    szClean = szClean.replace('Using ', '')
    
    # Skip if it's just a generic message
    if szClean.lower() in ['run in terminal', 'replace string in file', 'insert edit into file']:
        return ""
    
    return szClean

def main():
    """Main function to convert chat JSON to Markdown"""
    import sys
    
    # Parse command line arguments
    if len(sys.argv) >= 2:
        szJsonPath = sys.argv[1]
        if len(sys.argv) >= 3:
            szOutputPath = sys.argv[2]
        else:
            szOutputPath = szJsonPath.replace('.json', '.md')
    else:
        szJsonPath = "chat.json"
        szOutputPath = "chat_conversation.md"
    
    print(f"Loading chat data from {szJsonPath}...")
    dictChatData = LoadJsonFile(szJsonPath)
    
    if not dictChatData:
        print("Failed to load chat data!")
        print("Usage: python ChatToMD.py [input.json] [output.md]")
        return
    
    print("Converting to Markdown format...")
    szMarkdown = ConvertChatToMarkdown(dictChatData)
    
    print(f"Saving to {szOutputPath}...")
    try:
        with open(szOutputPath, 'w', encoding='utf-8') as file:
            file.write(szMarkdown)
        print(f"✅ Successfully converted chat to {szOutputPath}")
        print(f"📄 Generated {len(szMarkdown.splitlines())} lines of Markdown")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    main()